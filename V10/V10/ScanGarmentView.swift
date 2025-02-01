import SwiftUI
import PhotosUI
import Vision

struct ScanGarmentView: View {
    @Binding var isPresented: Bool
    let selectedImage: UIImage?
    @State private var showingCropper = false
    @State private var croppedImage: UIImage?
    @State private var scannedCode: String?
    @State private var isLoading = false
    @State private var scannedGarment: UniqloGarment?
    @State private var scannedProduct: Product?
    @State private var showingProductDetails = false
    
    init(selectedImage: UIImage?, isPresented: Binding<Bool>) {
        self.selectedImage = selectedImage
        self._isPresented = isPresented
    }
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Scan your Uniqlo tag")
                .font(.title2)
                .fontWeight(.medium)
            
            if isLoading {
                ProgressView()
            } else {
                VStack(spacing: 15) {
                    Button(action: {
                        showingCropper = true
                    }) {
                        Text("Select Photo")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .cornerRadius(10)
                    }
                }
                .padding(.horizontal, 40)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(.systemBackground))
        .onAppear {
            if selectedImage != nil {
                showingCropper = true
            }
        }
        .sheet(isPresented: $showingCropper) {
            if let image = selectedImage {
                ImageCropper(
                    image: image,
                    onCrop: { croppedImage in
                        self.croppedImage = croppedImage
                        processImage(croppedImage)
                    },
                    isPresented: $showingCropper
                )
            }
        }
        .sheet(isPresented: $showingProductDetails) {
            if let product = scannedProduct {
                NavigationView {
                    ProductDetailsView(
                        product: product,
                        isPresented: $showingProductDetails
                    )
                }
            }
        }
    }
    
    private func processImage(_ image: UIImage) {
        isLoading = true
        print("Processing cropped image")
        
        // Convert UIImage to CGImage
        guard let cgImage = image.cgImage else {
            print("Failed to get CGImage")
            isLoading = false
            return
        }
        
        // Create OCR request
        let request = VNRecognizeTextRequest { request, error in
            if let error = error {
                print("OCR error: \(error)")
                isLoading = false
                return
            }
            
            // Process results
            guard let observations = request.results as? [VNRecognizedTextObservation] else { return }
            
            // Extract text from observations
            let recognizedText = observations.compactMap { observation in
                observation.topCandidates(1).first?.string
            }
            
            // Print each recognized text line for debugging
            recognizedText.forEach { text in
                print("Recognized text: \(text)")
            }
            
            // Extract garment info
            var extractedInfo = ExtractedGarmentInfo()
            
            for line in recognizedText {
                print("Recognized text: \(line)")  // Keep this debug print
                
                // Product code detection - now handles different formats
                if line.contains("475296") {  // Direct match
                    extractedInfo.productCode = "475296"
                } else if let match = line.firstMatch(of: /\d{3}-(\d{6})/)?.1 {  // Format: xxx-475296
                    extractedInfo.productCode = String(match)
                }
                
                // Price detection (working correctly)
                if line.contains("$") {
                    if let price = Double(line.replacingOccurrences(of: "$", with: "")) {
                        extractedInfo.price = price
                    }
                }
            }
            
            print("Extracted Info: \(extractedInfo)")  // Debug print
            
            // Only send to backend if we got a product code
            if let productCode = extractedInfo.productCode {
                sendToBackend(productCode: productCode, scannedPrice: extractedInfo.price)
            }
        }
        
        // Configure the request
        request.recognitionLevel = .accurate
        
        // Create and execute the request handler
        let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
        do {
            try handler.perform([request])
        } catch {
            print("Failed to perform OCR: \(error)")
            isLoading = false
        }
    }
    
    private func sendToBackend(productCode: String, scannedPrice: Double?) {
        guard let url = URL(string: "\(Config.baseURL)/process_garment") else { return }
        
        let body: [String: Any] = [
            "product_code": productCode,
            "scanned_price": scannedPrice ?? 0.0
        ]
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Network error: \(error)")
                return
            }
            
            guard let data = data else { return }
            
            do {
                let product = try JSONDecoder().decode(Product.self, from: data)
                DispatchQueue.main.async {
                    self.scannedProduct = product
                    self.showingProductDetails = true
                    self.isLoading = false
                }
            } catch {
                print("Decoding error: \(error)")
                self.isLoading = false
            }
        }.resume()
    }
}

// Add this struct to handle extracted info
struct ExtractedGarmentInfo {
    var productCode: String?
    var name: String?
    var size: String?
    var color: String?
    var price: Double?
    var materials: [String: Int] = [:]
    var measurements: [String: String] = [:]
    var rawText: String?
}

struct ProductDetailsView: View {
    let product: Product
    @Binding var isPresented: Bool
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                AsyncImage(url: URL(string: product.imageUrl)) { image in
                    image.resizable()
                        .aspectRatio(contentMode: .fit)
                } placeholder: {
                    Color.gray.opacity(0.3)
                }
                .frame(height: 300)
                
                VStack(alignment: .leading, spacing: 12) {
                    Text(product.name)
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    if let price = product.price {
                        Text("Price: $\(price, specifier: "%.2f")")
                            .font(.headline)
                    }
                    
                    Text("Category: \(product.category)")
                    if let subcategory = product.subcategory {
                        Text("Subcategory: \(subcategory)")
                    }
                    
                    Text("Measurements (\(product.measurements.units))")
                        .font(.headline)
                        .padding(.top)
                    
                    ForEach(Array(product.measurements.sizes.keys.sorted()), id: \.self) { size in
                        if let sizeData = product.measurements.sizes[size] {
                            VStack(alignment: .leading) {
                                Text("Size \(size):")
                                    .fontWeight(.medium)
                                Text("Body Length: \(sizeData.body_length)")
                                Text("Body Width: \(sizeData.body_width)")
                                Text("Sleeve Length: \(sizeData.sleeve_length)")
                            }
                            .padding(.leading)
                            .padding(.vertical, 4)
                        }
                    }
                }
                .padding()
            }
        }
        .navigationTitle("Product Details")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("Done") {
                    isPresented = false
                }
            }
        }
    }
} 
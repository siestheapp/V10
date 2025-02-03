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
        NavigationView {
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
            .navigationBarItems(trailing: Button("Done") {
                isPresented = false
            })
        }
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
                .interactiveDismissDisabled()
                .presentationDragIndicator(.visible)
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
            print("\n--- Starting OCR Processing ---")
            
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
            
            print("\nAll recognized lines:")
            recognizedText.enumerated().forEach { index, line in
                print("[\(index)]: '\(line)'")  // Print with quotes to see whitespace
            }
            
            // Extract garment info
            var extractedInfo = ExtractedGarmentInfo(
                productCode: nil,
                name: nil,
                size: nil,
                color: nil,
                price: nil,
                materials: [:],
                measurements: [:],
                rawText: nil
            )
            
            for line in recognizedText {
                print("\nChecking line: '\(line)'")  // Print with quotes
                
                // Product code - look for xxx-xxxxxx pattern
                if let match = line.firstMatch(of: /\d{3}-(\d{6})/)?.1 {
                    extractedInfo.productCode = String(match)
                    print("Found product code: \(String(match))")
                }
                
                // Size detection - multiple approaches
                if line == "L" {
                    extractedInfo.size = "L"
                    print("Found size (exact match): L")
                }
                else if line.trimmingCharacters(in: .whitespaces) == "L" {
                    extractedInfo.size = "L"
                    print("Found size (trimmed): L")
                }
                else if line.contains("L") && !line.contains("LONG") && !line.contains("POLYESTER") {
                    extractedInfo.size = "L"
                    print("Found size (contains L): L")
                }
                
                // Price - look for dollar amount
                if line.hasPrefix("$") {
                    if let price = Double(line.replacingOccurrences(of: "$", with: "")) {
                        extractedInfo.price = price
                        print("Found price: \(price)")
                    }
                }
                
                // Color - look for color with number prefix
                if let colorMatch = line.firstMatch(of: /\d{2}\s+([A-Za-z\s]+)/)?.1 {
                    extractedInfo.color = String(colorMatch)
                    print("Found color: \(colorMatch)")
                }
                
                // Name - look for product name in all caps
                if line.contains("CREW NECK") || line.contains("SWEATER") || 
                   line.contains("T-SHIRT") {
                    extractedInfo.name = line
                    print("Found name: \(line)")
                }
            }
            
            // Add final debug print
            print("\nFinal extracted info:")
            print("Size: \(extractedInfo.size ?? "nil")")
            print("Product Code: \(extractedInfo.productCode ?? "nil")")
            print("Price: \(extractedInfo.price ?? 0.0)")
            
            // Only send to backend if we got a product code
            if let productCode = extractedInfo.productCode {
                sendToBackend(
                    productCode: productCode,
                    scannedPrice: extractedInfo.price,
                    scannedSize: extractedInfo.size
                )
            }
        }
        
        // Configure the request
        request.recognitionLevel = .accurate
        request.recognitionLanguages = ["en-US"]
        request.usesLanguageCorrection = false  // Add this to prevent correction
        request.minimumTextHeight = 0.1  // Add this to catch smaller text
        
        // Optional: Add custom recognition constraints
        let customWords = ["XS", "S", "M", "L", "XL", "XXL"]
        request.customWords = customWords
        
        // Create and execute the request handler
        let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
        do {
            try handler.perform([request])
        } catch {
            print("Failed to perform OCR: \(error)")
            isLoading = false
        }
    }
    
    private func sendToBackend(productCode: String, scannedPrice: Double?, scannedSize: String?) {
        guard let url = URL(string: "\(Config.baseURL)/process_garment") else { return }
        
        let body: [String: Any] = [
            "product_code": productCode,
            "scanned_price": scannedPrice ?? 0.0,
            "scanned_size": scannedSize
        ]
        
        print("Sending to backend:", body)  // Add this debug line
        
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
            
            if let jsonString = String(data: data, encoding: .utf8) {
                print("Server response: \(jsonString)")
            }
            
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

struct ScanGarmentView_Previews: PreviewProvider {
    static var previews: some View {
        ScanGarmentView(
            selectedImage: UIImage(systemName: "photo") ?? UIImage(),
            isPresented: .constant(true)
        )
    }
} 


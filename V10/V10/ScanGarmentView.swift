import SwiftUI
import PhotosUI
import Vision

struct ScanGarmentView: View {
    @State private var showingScanner = false
    @State private var showingImagePicker = false
    @State private var scannedCode: String?
    @State private var scannedGarment: UniqloGarment?
    @State private var isLoading = false
    @State private var selectedItem: PhotosPickerItem?
    @State private var selectedImage: UIImage?
    @State private var showingCropper = false
    @State private var croppedImage: UIImage?
    @Environment(\.dismiss) private var dismiss
    @State private var showingGarmentDetail = false
    
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
                        showingScanner = true
                    }) {
                        HStack {
                            Image(systemName: "barcode.viewfinder")
                                .font(.system(size: 24))
                            Text("Scan Tag")
                        }
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(10)
                    }
                    
                    PhotosPicker(
                        selection: $selectedItem,
                        matching: .images,
                        photoLibrary: .shared()
                    ) {
                        HStack {
                            Image(systemName: "photo.on.rectangle")
                                .font(.system(size: 24))
                            Text("Choose from Photos")
                        }
                        .foregroundColor(.blue)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.white)
                        .cornerRadius(10)
                        .overlay(
                            RoundedRectangle(cornerRadius: 10)
                                .stroke(Color.blue, lineWidth: 1)
                        )
                    }
                }
                .padding(.horizontal, 40)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(.systemBackground))
        .sheet(isPresented: $showingGarmentDetail) {
            if let garment = scannedGarment {
                NavigationView {
                    GarmentDetailView(garment: garment)
                }
            }
        }
        .sheet(isPresented: $showingScanner) {
            BarcodeScannerView(scannedCode: $scannedCode)
        }
        .sheet(isPresented: $showingCropper) {
            if let image = selectedImage {
                ImageCropperView(image: image, croppedImage: $croppedImage)
            }
        }
        .onChange(of: selectedItem) { oldValue, newItem in
            print("1. Photo selection changed")
            selectedImage = nil
            croppedImage = nil
            
            guard let item = newItem else {
                print("No item selected")
                return
            }
            
            Task {
                print("2. Starting image load")
                do {
                    guard let imageData = try await item.loadTransferable(type: Data.self) else {
                        print("Failed to load image data")
                        return
                    }
                    
                    print("3. Image data loaded: \(imageData.count) bytes")
                    
                    guard let uiImage = UIImage(data: imageData) else {
                        print("Failed to create UIImage")
                        return
                    }
                    
                    print("4. UIImage created")
                    
                    // Resize image before showing cropper
                    let resized = resizeImage(uiImage, targetSize: CGSize(width: 1024, height: 1024))
                    print("5. Image resized")
                    
                    await MainActor.run {
                        print("6. Setting selectedImage and showing cropper")
                        selectedImage = resized
                        showingCropper = true
                        print("7. Cropper should be visible now")
                    }
                } catch {
                    print("Error loading photo: \(error)")
                }
            }
        }
        .onChange(of: showingCropper) { oldValue, isShowing in
            print("Cropper sheet isShowing: \(isShowing)")
        }
        .onChange(of: croppedImage) { oldValue, newImage in
            print("Cropped image changed")
            if let image = newImage {
                print("Processing cropped image")
                detectBarcodeAndText(in: image)
            }
        }
        .onChange(of: scannedCode) { oldValue, newCode in
            if let code = newCode {
                lookupGarment(code: code)
            }
        }
        .onChange(of: scannedGarment) { garment in
            if garment != nil {
                showingGarmentDetail = true
            }
        }
    }
    
    private func lookupGarment(code: String) {
        isLoading = true
        guard let url = URL(string: "http://127.0.0.1:8000/garment/\(code)") else {
            isLoading = false
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            defer { isLoading = false }
            
            if let data = data {
                do {
                    let garment = try JSONDecoder().decode(UniqloGarment.self, from: data)
                    DispatchQueue.main.async {
                        self.scannedGarment = garment
                    }
                } catch {
                    print("Decoding error: \(error)")
                }
            }
        }.resume()
    }
    
    private func performOCR(from image: UIImage, completion: @escaping (String?) -> Void) {
        guard let cgImage = image.cgImage else {
            completion(nil)
            return
        }

        // Create a new request to recognize text
        let request = VNRecognizeTextRequest { request, error in
            if let error = error {
                print("OCR Error: \(error)")
                completion(nil)
                return
            }

            // Process the results
            var fullText = ""
            if let observations = request.results as? [VNRecognizedTextObservation] {
                for observation in observations {
                    // Get the top candidate string for each observation
                    if let topCandidate = observation.topCandidates(1).first {
                        fullText += topCandidate.string + "\n"
                        print("Recognized text: \(topCandidate.string)")
                    }
                }
                completion(fullText)
            } else {
                completion(nil)
            }
        }

        // Configure the request
        request.recognitionLevel = .accurate
        request.recognitionLanguages = ["en-US"]
        request.usesLanguageCorrection = true
        
        // Create an image request handler and perform the request
        let requestHandler = VNImageRequestHandler(cgImage: cgImage, options: [:])
        do {
            try requestHandler.perform([request])
        } catch {
            print("Failed to perform OCR: \(error)")
            completion(nil)
        }
    }
    
    private func detectBarcodeAndText(in image: UIImage) {
        print("Starting detection")
        
        // First try barcode detection
        let barcodeRequest = VNDetectBarcodesRequest { request, error in
            if let results = request.results as? [VNBarcodeObservation],
               let firstBarcode = results.first,
               let payload = firstBarcode.payloadStringValue {
                print("Found barcode: \(payload)")
                DispatchQueue.main.async {
                    self.scannedCode = payload
                }
                return
            }
            
            // If no barcode found, try OCR
            print("No barcode found, trying OCR")
            self.performOCR(from: image) { recognizedText in
                guard let text = recognizedText else { return }
                self.processExtractedText(text)
            }
        }
        
        // Configure and perform the barcode request
        barcodeRequest.symbologies = [.ean13, .ean8, .qr, .code128]
        
        guard let cgImage = image.cgImage else { return }
        let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
        
        do {
            try handler.perform([barcodeRequest])
        } catch {
            print("Detection error: \(error)")
        }
    }
    
    // Helper function to maintain aspect ratio while resizing
    private func resizeImage(_ image: UIImage, targetSize: CGSize) -> UIImage {
        let size = image.size
        let widthRatio = targetSize.width / size.width
        let heightRatio = targetSize.height / size.height
        let ratio = min(widthRatio, heightRatio)
        
        let newSize = CGSize(width: size.width * ratio, height: size.height * ratio)
        let rect = CGRect(x: 0, y: 0, width: newSize.width, height: newSize.height)
        
        UIGraphicsBeginImageContextWithOptions(newSize, false, 1.0)
        image.draw(in: rect)
        let newImage = UIGraphicsGetImageFromCurrentImageContext()
        UIGraphicsEndImageContext()
        
        return newImage ?? image
    }
    
    private func processExtractedText(_ text: String) {
        var extractedInfo = ExtractedGarmentInfo()
        extractedInfo.rawText = text
        
        let lines = text.components(separatedBy: .newlines)
        var fullName = [String]()
        
        for line in lines {
            let trimmedLine = line.trimmingCharacters(in: .whitespaces)
            
            // Product code detection (updated to include Uniqlo's format)
            if trimmedLine.matches(of: /\d{13}/).count > 0 {  // EAN-13 format
                extractedInfo.productCode = trimmedLine
            } else if trimmedLine.matches(of: /[A-Z]{2}\d{5}[A-Z]{2}-[A-Z]{2}/).count > 0 {  // HT00189FT-US format
                extractedInfo.productCode = trimmedLine
            } else if trimmedLine.matches(of: /S\d{3}-\d{4}/).count > 0 {  // S202-4575 format
                extractedInfo.productCode = trimmedLine
            } else if trimmedLine.matches(of: /\d{6}/).count > 0 {  // 475296 format
                if let match = trimmedLine.firstMatch(of: /\d{6}/) {
                    extractedInfo.productCode = String(match.0)
                }
            } else if trimmedLine.matches(of: /\d{3}-\d{6}/).count > 0 {  // Add: 341-469922 format
                if let match = trimmedLine.firstMatch(of: /\d{6}$/) {  // Get last 6 digits
                    extractedInfo.productCode = String(match.0)
                }
            }
            
            // Product name detection
            if trimmedLine.contains("KNIT") || trimmedLine.contains("SWEATER") || 
               trimmedLine.contains("SHIRT") || trimmedLine.contains("PANTS") {
                fullName.append(trimmedLine)
            }
            
            // Size detection
            if trimmedLine.matches(of: /^[XS|S|M|L|XL]$/).count > 0 {
                extractedInfo.size = trimmedLine
            }
            
            // Color detection (includes color code)
            if trimmedLine.matches(of: /\d{2}\s+[A-Za-z]+/).count > 0 {
                extractedInfo.color = trimmedLine
            }
            
            // Price detection
            if trimmedLine.contains("$") {
                if let price = Double(trimmedLine.replacingOccurrences(of: "$", with: "").trimmingCharacters(in: .whitespaces)) {
                    extractedInfo.price = price
                }
            }
            
            // Materials detection
            if trimmedLine.contains("%") {
                let components = trimmedLine.components(separatedBy: " ")
                if components.count >= 2,
                   let percentage = Int(components[0].replacingOccurrences(of: "%", with: "")),
                   let material = components.last {
                    extractedInfo.materials[material] = percentage
                }
            }
            
            // Measurements detection
            if trimmedLine.contains("inch") || trimmedLine.contains("\"") {
                if trimmedLine.contains("Chest") {
                    let measurement = trimmedLine.replacingOccurrences(of: "Chest", with: "")
                        .replacingOccurrences(of: "inch", with: "")
                        .replacingOccurrences(of: "\"", with: "")
                        .trimmingCharacters(in: .whitespaces)
                    extractedInfo.measurements["chest"] = measurement
                }
            }
        }
        
        // Combine name parts
        if !fullName.isEmpty {
            extractedInfo.name = fullName.joined(separator: " ")
        }
        
        print("Extracted Info: \(extractedInfo)")  // Debug print
        sendToBackend(extractedInfo)
    }
    
    private func sendToBackend(_ info: ExtractedGarmentInfo) {
        guard let url = URL(string: "http://127.0.0.1:8000/process_garment") else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            let jsonData = try JSONEncoder().encode(info)
            print("Sending to backend: \(String(data: jsonData, encoding: .utf8) ?? "")")  // Debug print
            request.httpBody = jsonData
            
            URLSession.shared.dataTask(with: request) { data, response, error in
                if let error = error {
                    print("Error sending to backend: \(error)")
                    return
                }
                
                if let data = data {
                    print("Received from backend: \(String(data: data, encoding: .utf8) ?? "")")  // Debug print
                    do {
                        let garment = try JSONDecoder().decode(UniqloGarment.self, from: data)
                        DispatchQueue.main.async {
                            self.scannedGarment = garment
                        }
                    } catch {
                        print("Decoding error: \(error)")
                        if let responseString = String(data: data, encoding: .utf8) {
                            print("Raw response: \(responseString)")
                        }
                    }
                }
            }.resume()
        } catch {
            print("Encoding error: \(error)")
        }
    }
}

#Preview {
    ScanGarmentView()
} 
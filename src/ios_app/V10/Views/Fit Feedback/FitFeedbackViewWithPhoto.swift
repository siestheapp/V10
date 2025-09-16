// FitFeedbackViewWithPhoto.swift
// Enhanced version of FitFeedbackView with photo capture capabilities

import SwiftUI
import PhotosUI

struct FitFeedbackViewWithPhoto: View {
    let feedbackType: FeedbackType
    let selectedSize: String
    let productUrl: String?
    let brand: String?
    let fitType: String?
    let selectedColor: String?
    
    @Environment(\.dismiss) private var dismiss
    @State private var fitFeedback: [String: Int] = [:]
    @State private var isSubmitting = false
    @State private var showConfirmation = false
    
    // Photo capture states
    @State private var showCamera = false
    @State private var showPhotoLibrary = false
    @State private var capturedImage: UIImage?
    @State private var selectedPhotoItem: PhotosPickerItem?
    @State private var photoCaption = ""
    @State private var isUploadingPhoto = false
    @State private var currentGarmentId: Int?
    
    // Initializers
    init(feedbackType: FeedbackType, selectedSize: String, productUrl: String? = nil, brand: String? = nil, fitType: String? = nil, selectedColor: String? = nil) {
        self.feedbackType = feedbackType
        self.selectedSize = selectedSize
        self.productUrl = productUrl
        self.brand = brand
        self.fitType = fitType
        self.selectedColor = selectedColor
    }

    let fitOptions = [
        (1, "Too Tight"),
        (2, "Tight but I Like It"),
        (3, "Great Fit"),
        (4, "Loose but I Like It"),
        (5, "Too Loose")
    ]

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Header
                VStack(spacing: 10) {
                    Text("Fit Feedback")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                    
                    Text(feedbackDescription)
                        .font(.subheadline)
                        .foregroundColor(.gray)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 30)
                }
                .padding(.top, 20)
                
                // Photo Section
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Image(systemName: "camera.fill")
                            .foregroundColor(.blue)
                        Text("Try-On Photo")
                            .font(.headline)
                    }
                    .padding(.horizontal)
                    
                    if let image = capturedImage {
                        // Show captured/selected image
                        VStack(spacing: 12) {
                            Image(uiImage: image)
                                .resizable()
                                .scaledToFit()
                                .frame(maxHeight: 300)
                                .cornerRadius(12)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 12)
                                        .stroke(Color.blue.opacity(0.3), lineWidth: 1)
                                )
                                .padding(.horizontal)
                            
                            VStack(spacing: 8) {
                                TextField("Add a note about the fit (optional)", text: $photoCaption)
                                    .textFieldStyle(RoundedBorderTextFieldStyle())
                                    .padding(.horizontal)
                                
                                Button(action: { 
                                    capturedImage = nil
                                    photoCaption = ""
                                }) {
                                    HStack {
                                        Image(systemName: "trash")
                                        Text("Remove Photo")
                                    }
                                    .foregroundColor(.red)
                                    .font(.caption)
                                }
                            }
                        }
                    } else {
                        // Photo capture buttons
                        HStack(spacing: 16) {
                            Button(action: { showCamera = true }) {
                                VStack(spacing: 8) {
                                    Image(systemName: "camera.fill")
                                        .font(.title2)
                                    Text("Take Photo")
                                        .font(.caption)
                                }
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.blue.opacity(0.1))
                                .cornerRadius(12)
                            }
                            
                            PhotosPicker(
                                selection: $selectedPhotoItem,
                                matching: .images
                            ) {
                                VStack(spacing: 8) {
                                    Image(systemName: "photo.fill")
                                        .font(.title2)
                                    Text("Choose Photo")
                                        .font(.caption)
                                }
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.green.opacity(0.1))
                                .cornerRadius(12)
                            }
                        }
                        .padding(.horizontal)
                        
                        Text("Optional: Add a photo to remember how this size looked on you")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .padding(.horizontal)
                            .padding(.top, 4)
                    }
                }
                .padding(.vertical)
                .background(Color(UIColor.systemGray6))
                .cornerRadius(12)
                .padding(.horizontal)
                
                // Fit Feedback Section
                VStack(alignment: .leading, spacing: 20) {
                    ForEach(getMeasurementsForFeedbackType(), id: \.self) { measurement in
                        VStack(alignment: .leading, spacing: 10) {
                            Text(measurement == "Overall" ? "How does it fit overall?" : "How does it fit in the \(measurement)?")
                                .font(.headline)
                                .padding(.horizontal)

                            ScrollView(.horizontal, showsIndicators: false) {
                                HStack(spacing: 10) {
                                    ForEach(fitOptions, id: \.0) { option in
                                        Button(action: {
                                            fitFeedback[measurement] = option.0
                                        }) {
                                            Text(option.1)
                                                .padding(.horizontal, 16)
                                                .padding(.vertical, 12)
                                                .background(fitFeedback[measurement] == option.0 ? Color.blue : Color.gray.opacity(0.2))
                                                .foregroundColor(fitFeedback[measurement] == option.0 ? .white : .primary)
                                                .cornerRadius(10)
                                        }
                                    }
                                }
                                .padding(.horizontal)
                            }
                        }
                        .padding(.vertical, 8)
                    }
                }
                
                // Submit Button
                Button(action: submitFeedback) {
                    if isSubmitting || isUploadingPhoto {
                        HStack {
                            ProgressView()
                                .scaleEffect(0.8)
                            Text(isUploadingPhoto ? "Uploading Photo..." : "Submitting...")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue.opacity(0.6))
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    } else {
                        Text("Submit Feedback")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .cornerRadius(12)
                    }
                }
                .padding(.horizontal, 40)
                .padding(.bottom, 20)
                .disabled(isSubmitting || isUploadingPhoto || fitFeedback.isEmpty)
            }
        }
        .sheet(isPresented: $showCamera) {
            CameraView(image: $capturedImage)
        }
        .onChange(of: selectedPhotoItem) { newItem in
            Task {
                if let data = try? await newItem?.loadTransferable(type: Data.self),
                   let uiImage = UIImage(data: data) {
                    await MainActor.run {
                        capturedImage = uiImage
                    }
                }
            }
        }
        .alert("Feedback Submitted", isPresented: $showConfirmation) {
            Button("OK", role: .cancel) { 
                dismiss()
            }
        } message: {
            Text("Thank you! Your feedback and photo have been saved.")
        }
    }
    
    private var feedbackDescription: String {
        switch feedbackType {
        case .manualEntry:
            let sizeAndFit = fitType != nil ? "\(selectedSize) \(fitType!)" : selectedSize
            return "Based on your selected size (\(sizeAndFit)), tell us how this garment fits."
        case .scannedGarment:
            return "We scanned your tag! Let us know how this garment fits to improve recommendations."
        case .newBrand:
            return "This is a new brand for us! Your feedback will help us improve future suggestions."
        case .specialFit:
            return "Some fabrics fit differently. Help us refine fit accuracy for stretch vs. rigid fabrics."
        }
    }

    private func getMeasurementsForFeedbackType() -> [String] {
        switch feedbackType {
        case .manualEntry:
            return ["Overall", "Chest", "Waist", "Sleeve"]
        case .scannedGarment:
            return ["Overall", "Chest", "Waist", "Sleeve", "Neck"]
        case .newBrand:
            return ["Overall", "Chest", "Waist", "Sleeve", "Shoulders"]
        case .specialFit:
            return ["Overall", "Chest", "Waist", "Hip", "Stretch Comfort"]
        }
    }
    
    private func submitFeedback() {
        isSubmitting = true
        
        var feedbackData: [String: Any] = [
            "user_id": "1",
            "session_id": "tryon_\(Int(Date().timeIntervalSince1970))",
            "product_url": productUrl ?? "",
            "brand_id": getBrandIdFromUrl(productUrl ?? ""),
            "size_tried": selectedSize,
            "feedback": fitFeedback
        ]
        
        if let fitType = fitType {
            feedbackData["fit_type"] = fitType
        }
        
        if let selectedColor = selectedColor {
            feedbackData["selected_color"] = selectedColor
        }
        
        guard let url = URL(string: "\(Config.baseURL)/tryon/submit") else {
            print("❌ Invalid API URL")
            isSubmitting = false
            return
        }
        
        guard let jsonData = try? JSONSerialization.data(withJSONObject: feedbackData) else {
            print("❌ Failed to encode feedback data")
            isSubmitting = false
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("❌ Network error: \(error.localizedDescription)")
                DispatchQueue.main.async {
                    self.isSubmitting = false
                }
                return
            }
            
            guard let data = data else {
                print("❌ No data received")
                DispatchQueue.main.async {
                    self.isSubmitting = false
                }
                return
            }
            
            do {
                let response = try JSONSerialization.jsonObject(with: data) as? [String: Any]
                print("✅ Feedback submitted: \(response ?? [:])")
                
                if let garmentId = response?["garment_id"] as? Int {
                    DispatchQueue.main.async {
                        self.currentGarmentId = garmentId
                        // Upload photo if we have one
                        if let image = self.capturedImage {
                            self.uploadPhoto(image: image, garmentId: garmentId)
                        } else {
                            // No photo to upload, show confirmation
                            self.isSubmitting = false
                            self.showConfirmation = true
                        }
                    }
                }
            } catch {
                print("❌ Failed to parse response: \(error.localizedDescription)")
                DispatchQueue.main.async {
                    self.isSubmitting = false
                }
            }
        }.resume()
    }
    
    private func uploadPhoto(image: UIImage, garmentId: Int) {
        isUploadingPhoto = true
        
        // Convert image to base64
        guard let imageData = image.jpegData(compressionQuality: 0.7) else {
            print("❌ Failed to convert image to data")
            isUploadingPhoto = false
            isSubmitting = false
            return
        }
        
        let base64String = imageData.base64EncodedString()
        
        let photoData: [String: Any] = [
            "user_id": "1",
            "photo_base64": "data:image/jpeg;base64,\(base64String)",
            "photo_type": "camera",
            "caption": photoCaption,
            "is_primary": true,
            "metadata": [
                "feedback_session": "tryon_\(Int(Date().timeIntervalSince1970))",
                "size": selectedSize,
                "fit_type": fitType ?? "",
                "color": selectedColor ?? ""
            ]
        ]
        
        guard let url = URL(string: "\(Config.baseURL)/garment/\(garmentId)/photos") else {
            print("❌ Invalid photo upload URL")
            isUploadingPhoto = false
            isSubmitting = false
            return
        }
        
        guard let jsonData = try? JSONSerialization.data(withJSONObject: photoData) else {
            print("❌ Failed to encode photo data")
            isUploadingPhoto = false
            isSubmitting = false
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                self.isUploadingPhoto = false
                self.isSubmitting = false
                
                if let error = error {
                    print("❌ Photo upload error: \(error.localizedDescription)")
                } else if let data = data {
                    do {
                        let response = try JSONSerialization.jsonObject(with: data)
                        print("✅ Photo uploaded: \(response)")
                    } catch {
                        print("❌ Failed to parse photo upload response")
                    }
                }
                
                // Show confirmation regardless of photo upload result
                self.showConfirmation = true
            }
        }.resume()
    }
    
    private func getBrandIdFromUrl(_ url: String) -> Int {
        let lowercaseUrl = url.lowercased()
        
        if lowercaseUrl.contains("jcrew.com") {
            return 4
        } else if lowercaseUrl.contains("lululemon.com") {
            return 1
        } else if lowercaseUrl.contains("bananarepublic.com") || lowercaseUrl.contains("bananarepublic.gap.com") {
            return 5
        } else if lowercaseUrl.contains("patagonia.com") {
            return 2
        } else if lowercaseUrl.contains("theory.com") {
            return 9
        } else if lowercaseUrl.contains("uniqlo.com") {
            return 21
        } else if lowercaseUrl.contains("nn07.com") {
            return 12
        } else if lowercaseUrl.contains("vuori.com") {
            return 18
        } else if lowercaseUrl.contains("lacoste.com") {
            return 11
        } else if lowercaseUrl.contains("reiss.com") {
            return 10
        } else if lowercaseUrl.contains("faherty.com") {
            return 8
        }
        
        return 4 // Default to J.Crew
    }
}

// Camera View for taking photos
struct CameraView: UIViewControllerRepresentable {
    @Binding var image: UIImage?
    @Environment(\.dismiss) private var dismiss
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = .camera
        picker.allowsEditing = true
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: CameraView
        
        init(_ parent: CameraView) {
            self.parent = parent
        }
        
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            if let editedImage = info[.editedImage] as? UIImage {
                parent.image = editedImage
            } else if let originalImage = info[.originalImage] as? UIImage {
                parent.image = originalImage
            }
            parent.dismiss()
        }
        
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.dismiss()
        }
    }
}

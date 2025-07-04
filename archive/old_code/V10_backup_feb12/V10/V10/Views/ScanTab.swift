import SwiftUI

struct ScanTab: View {
    @State private var showingOptions = false
    @State private var showingImagePicker = false
    @State private var showingScanView = false
    @State private var selectedImage: UIImage?
    
    var body: some View {
        VStack(spacing: 30) {
            Text("Scan")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            Button(action: {
                showingOptions = true
            }) {
                Text("Scan a Tag")
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(10)
            }
            .padding(.horizontal, 40)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(.systemBackground))
        .confirmationDialog("Choose an option", isPresented: $showingOptions) {
            Button("Open Camera") {
                showingImagePicker = true
            }
            
            Button("Choose from Photos") {
                showingImagePicker = true
            }
        }
        .sheet(isPresented: $showingImagePicker) {
            ImagePicker(image: $selectedImage)
        }
        .onChange(of: selectedImage) { newImage in
            if newImage != nil {
                showingScanView = true
            }
        }
        .sheet(isPresented: $showingScanView) {
            if let image = selectedImage {
                NavigationView {
                    ScanGarmentView(
                        selectedImage: image,
                        isPresented: $showingScanView
                    )
                }
            }
        }
    }
}

#Preview {
    ScanTab()
} 
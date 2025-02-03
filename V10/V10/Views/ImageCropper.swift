import SwiftUI

struct ImageCropper: View {
    let image: UIImage
    let onCrop: (UIImage) -> Void
    @Binding var isPresented: Bool
    
    var body: some View {
        NavigationView {
            VStack {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
                    .padding()
                
                Button(action: {
                    onCrop(image)  // Pass the image to be processed
                    isPresented = false  // Dismiss the cropper
                }) {
                    Text("Scan Tag")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(10)
                }
                .padding(.horizontal, 40)
                .padding(.bottom, 20)
            }
            .navigationTitle("Crop Tag")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        isPresented = false
                    }
                }
            }
        }
    }
}

#Preview {
    ImageCropper(
        image: UIImage(systemName: "photo") ?? UIImage(),
        onCrop: { _ in },
        isPresented: .constant(true)
    )
} 
import SwiftUI

struct ImageCropperView: View {
    let image: UIImage
    @Binding var croppedImage: UIImage?
    @Environment(\.dismiss) private var dismiss
    
    @State private var cropRect: CGRect = .zero
    @State private var isLoading = false
    
    // Corner positions
    @State private var topLeft: CGPoint = .zero
    @State private var topRight: CGPoint = .zero
    @State private var bottomLeft: CGPoint = .zero
    @State private var bottomRight: CGPoint = .zero
    
    // Add minimum size constraint
    private let minSize: CGFloat = 100
    
    // Add drag state to track corner being dragged
    @State private var draggedCorner: Corner = .none
    
    enum Corner {
        case topLeft, topRight, bottomLeft, bottomRight, none
    }
    
    var body: some View {
        VStack(spacing: 0) {
            Text("Drag corners to crop")
                .font(.headline)
                .padding()
                .foregroundColor(.white)
            
            GeometryReader { geometry in
                ZStack {
                    // Background
                    Color.black
                    
                    // Image
                    Image(uiImage: image)
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                    
                    // Overlay
                    Rectangle()
                        .fill(Color.black.opacity(0.5))
                        .overlay(
                            Rectangle()
                                .stroke(Color.white, lineWidth: 2)
                                .frame(width: cropRect.width, height: cropRect.height)
                        )
                        .mask(
                            Rectangle()
                                .overlay(
                                    Rectangle()
                                        .frame(width: cropRect.width, height: cropRect.height)
                                        .position(x: cropRect.midX, y: cropRect.midY)
                                        .blendMode(.destinationOut)
                                )
                        )
                    
                    // Update corner handles
                    Group {
                        // Top left
                        Circle()
                            .fill(Color.white)
                            .frame(width: 20, height: 20)
                            .position(topLeft)
                            .gesture(
                                DragGesture()
                                    .onChanged { value in
                                        let newPos = value.location
                                        // Constrain to keep within bounds and maintain minimum size
                                        let maxX = topRight.x - minSize
                                        let maxY = bottomLeft.y - minSize
                                        let x = min(maxX, max(0, newPos.x))
                                        let y = min(maxY, max(0, newPos.y))
                                        topLeft = CGPoint(x: x, y: y)
                                        // Update opposite corners Y position
                                        topRight.y = y
                                        // Update opposite corners X position
                                        bottomLeft.x = x
                                        updateCropRect()
                                    }
                            )
                        
                        // Top right
                        Circle()
                            .fill(Color.white)
                            .frame(width: 20, height: 20)
                            .position(topRight)
                            .gesture(
                                DragGesture()
                                    .onChanged { value in
                                        let newPos = value.location
                                        let minX = topLeft.x + minSize
                                        let maxY = bottomRight.y - minSize
                                        let x = max(minX, min(geometry.size.width, newPos.x))
                                        let y = min(maxY, max(0, newPos.y))
                                        topRight = CGPoint(x: x, y: y)
                                        topLeft.y = y
                                        bottomRight.x = x
                                        updateCropRect()
                                    }
                            )
                        
                        // Bottom left
                        Circle()
                            .fill(Color.white)
                            .frame(width: 20, height: 20)
                            .position(bottomLeft)
                            .gesture(
                                DragGesture()
                                    .onChanged { value in
                                        let newPos = value.location
                                        let maxX = bottomRight.x - minSize
                                        let minY = topLeft.y + minSize
                                        let x = min(maxX, max(0, newPos.x))
                                        let y = max(minY, min(geometry.size.height, newPos.y))
                                        bottomLeft = CGPoint(x: x, y: y)
                                        bottomRight.y = y
                                        topLeft.x = x
                                        updateCropRect()
                                    }
                            )
                        
                        // Bottom right
                        Circle()
                            .fill(Color.white)
                            .frame(width: 20, height: 20)
                            .position(bottomRight)
                            .gesture(
                                DragGesture()
                                    .onChanged { value in
                                        let newPos = value.location
                                        let minX = bottomLeft.x + minSize
                                        let minY = topRight.y + minSize
                                        let x = max(minX, min(geometry.size.width, newPos.x))
                                        let y = max(minY, min(geometry.size.height, newPos.y))
                                        bottomRight = CGPoint(x: x, y: y)
                                        bottomLeft.y = y
                                        topRight.x = x
                                        updateCropRect()
                                    }
                            )
                    }
                }
                .onAppear {
                    // Initialize crop rect
                    let width = geometry.size.width * 0.8
                    let height = width * 1.5 // For tag aspect ratio
                    let x = (geometry.size.width - width) / 2
                    let y = (geometry.size.height - height) / 2
                    cropRect = CGRect(x: x, y: y, width: width, height: height)
                    updateCornerPositions()
                }
            }
            
            HStack(spacing: 30) {
                Button("Cancel") {
                    dismiss()
                }
                .foregroundColor(.red)
                .padding()
                
                Button {
                    isLoading = true
                    cropImage()
                    dismiss()
                } label: {
                    if isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .blue))
                    } else {
                        Text("Crop")
                            .foregroundColor(.blue)
                    }
                }
                .padding()
                .disabled(isLoading)
            }
            .padding(.bottom)
        }
        .background(Color.black)
        .edgesIgnoringSafeArea(.all)
    }
    
    private func updateCornerPositions() {
        topLeft = CGPoint(x: cropRect.minX, y: cropRect.minY)
        topRight = CGPoint(x: cropRect.maxX, y: cropRect.minY)
        bottomLeft = CGPoint(x: cropRect.minX, y: cropRect.maxY)
        bottomRight = CGPoint(x: cropRect.maxX, y: cropRect.maxY)
    }
    
    private func updateCropRect() {
        let minX = min(topLeft.x, bottomLeft.x)
        let maxX = max(topRight.x, bottomRight.x)
        let minY = min(topLeft.y, topRight.y)
        let maxY = max(bottomLeft.y, bottomRight.y)
        
        cropRect = CGRect(x: minX, y: minY, width: maxX - minX, height: maxY - minY)
    }
    
    private func cropImage() {
        let scale = image.size.width / UIScreen.main.bounds.width
        let scaledRect = CGRect(x: cropRect.origin.x * scale,
                              y: cropRect.origin.y * scale,
                              width: cropRect.width * scale,
                              height: cropRect.height * scale)
        
        if let cgImage = image.cgImage?.cropping(to: scaledRect) {
            croppedImage = UIImage(cgImage: cgImage)
        }
    }
}

#Preview("Default State") {
    ImageCropperView(
        image: UIImage(systemName: "tag.fill")!
            .withTintColor(.blue, renderingMode: .alwaysOriginal),
        croppedImage: .constant(nil)
    )
}

#Preview("With Sample Tag") {
    ImageCropperView(
        image: UIImage(systemName: "tag.fill")!
            .withTintColor(.blue, renderingMode: .alwaysOriginal),
        croppedImage: .constant(nil)
    )
} 
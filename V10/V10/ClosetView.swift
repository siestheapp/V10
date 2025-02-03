import SwiftUI
import PhotosUI

struct ClosetView: View {
    @State private var showingScanView = false
    @State private var showingOptions = false
    @State private var showingImagePicker = false
    @State private var selectedImage: UIImage?
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Scan Tab
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
            .tabItem {
                Label("Scan", systemImage: "camera")
            }
            .tag(0)
            
            // Finds Tab
            ScanHistoryView()
                .tabItem {
                    Label("Finds", systemImage: "list.bullet")
                }
                .tag(1)
        }
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
    ClosetView()
} 
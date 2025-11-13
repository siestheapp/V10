import SwiftUI

// Ultra-optimized version with NO hangs or delays
struct UltraOptimizedScanTab: View {
    @State private var productLink = ""
    @State private var isAnalyzing = false
    @FocusState private var isTextFieldFocused: Bool
    
    var body: some View {
        // REMOVED NavigationStack - might be causing the hang
        VStack(spacing: 0) {
            // Simple header
            Text("Find Your Fit")
                .font(.largeTitle)
                .fontWeight(.bold)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding()
            
            ScrollView {
                VStack(spacing: 20) {
                    // Simple scan button
                    Button(action: {}) {
                        HStack {
                            Image(systemName: "camera.fill")
                            Text("Scan a Tag")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }
                    .padding(.horizontal)
                    
                    Text("OR")
                        .foregroundColor(.secondary)
                    
                    // ULTRA SIMPLE TEXT FIELD - NO DECORATIONS
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Paste Product Link")
                            .font(.headline)
                            .padding(.horizontal)
                        
                        TextField("Enter URL here", text: $productLink)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .focused($isTextFieldFocused)
                            .padding(.horizontal)
                        
                        if !productLink.isEmpty {
                            Button(action: { analyzeProduct() }) {
                                Text("Get Size Recommendation")
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(Color.blue)
                                    .foregroundColor(.white)
                                    .cornerRadius(12)
                            }
                            .padding(.horizontal)
                            .disabled(isAnalyzing)
                        }
                    }
                    
                    if isAnalyzing {
                        ProgressView("Analyzing...")
                            .padding()
                    }
                    
                    Spacer(minLength: 100)
                }
                .padding(.vertical)
            }
        }
        .background(Color(.systemGroupedBackground))
    }
    
    private func analyzeProduct() {
        guard !productLink.isEmpty else { return }
        
        isAnalyzing = true
        
        // Simulate network call
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            self.isAnalyzing = false
        }
    }
}

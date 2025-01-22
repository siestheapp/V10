import SwiftUI

struct MeasurementIntroView: View {
    @State private var showMeasurementOptions = false
    
    var body: some View {
        if showMeasurementOptions {
            MeasurementOptionsView()
        } else {
            VStack(spacing: 30) {
                Text("Sies predicts how clothes will fit you after determining your measurements.")
                    .font(.title2)
                    .fontWeight(.medium)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 40)
                
                Button(action: {
                    withAnimation {
                        showMeasurementOptions = true
                    }
                }) {
                    Text("Continue")
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
        }
    }
}

struct MeasurementOptionsView: View {
    @State private var showingScanView = false
    
    var body: some View {
        if showingScanView {
            ScanGarmentView()
        } else {
            VStack(spacing: 30) {
                Text("To start the measurement process, you can:")
                    .font(.title2)
                    .fontWeight(.medium)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 40)
                
                VStack(spacing: 15) {
                    Button(action: {
                        // Handle input clothes action
                    }) {
                        Text("Input clothes that fit you well")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .cornerRadius(10)
                    }
                    
                    Button(action: {
                        withAnimation {
                            showingScanView = true
                        }
                    }) {
                        Text("Try something on and tell us how it fits")
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
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Color(.systemBackground))
        }
    }
}

struct MeasurementIntroView_Previews: PreviewProvider {
    static var previews: some View {
        Group {
            MeasurementIntroView()
                .previewDisplayName("Intro Screen")
            
            MeasurementOptionsView()
                .previewDisplayName("Options Screen")
        }
    }
} 
import SwiftUI

struct FeedbackSheet: View {
    let measurement: BrandMeasurement
    @Binding var isPresented: Bool
    @State private var selectedFitType: FitType = .regular
    @State private var selectedGarmentType: GarmentType?
    @State private var customFeedback: String = ""
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("GARMENT INFO")) {
                    Text(measurement.brand)
                        .font(.headline)
                    Text(measurement.garmentName)
                        .foregroundColor(.gray)
                }
                
                Section(header: Text("FIT TYPE")) {
                    Picker("Fit", selection: $selectedFitType) {
                        ForEach(FitType.allCases, id: \.self) { fit in
                            Text(fit.rawValue).tag(fit)
                        }
                    }
                    .pickerStyle(.segmented)
                }
                
                Section(header: Text("GARMENT TYPE")) {
                    ForEach(GarmentType.allCases, id: \.self) { type in
                        HStack {
                            Text(type.rawValue)
                            Spacer()
                            if selectedGarmentType == type {
                                Image(systemName: "checkmark")
                                    .foregroundColor(.blue)
                            }
                        }
                        .contentShape(Rectangle())
                        .onTapGesture {
                            selectedGarmentType = type
                        }
                    }
                }
                
                Section(header: Text("ADDITIONAL FEEDBACK")) {
                    TextEditor(text: $customFeedback)
                        .frame(height: 100)
                }
            }
            .navigationTitle("Fit Feedback")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        isPresented = false
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        saveFeedback()
                        isPresented = false
                    }
                }
            }
        }
    }
    
    private func saveFeedback() {
        let feedback = FitFeedback(
            brand: measurement.brand,
            garmentName: measurement.garmentName,
            size: measurement.size,
            fitType: selectedFitType,
            garmentType: selectedGarmentType,
            customFeedback: customFeedback.isEmpty ? nil : customFeedback
        )
        
        // TODO: Save feedback to server
        print("Saving feedback:", feedback)
    }
}

#Preview {
    FeedbackSheet(
        measurement: BrandMeasurement(
            brand: "J.Crew",
            garmentName: "Cotton Sweater",
            measurementRange: MeasurementRange(min: 41, max: 43),
            size: "L",
            ownsGarment: true,
            fitContext: nil,
            userFeedback: nil,
            confidence: 0.9
        ),
        isPresented: .constant(true)
    )
} 
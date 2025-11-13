import SwiftUI

struct MeasurementDetailRow: View {
    let measurement: BrandMeasurement
    @State private var showingFeedbackSheet = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                VStack(alignment: .leading) {
                    Text(measurement.brand)
                        .font(.subheadline)
                        .fontWeight(.medium)
                    Text(measurement.garmentName)
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                Spacer()
                if measurement.measurementRange.min == measurement.measurementRange.max {
                    Text(String(format: "%.1f\"", measurement.measurementRange.min))
                } else {
                    Text(String(format: "%.1f-%.1f\"", 
                         measurement.measurementRange.min,
                         measurement.measurementRange.max))
                }
            }
            
            if let context = measurement.fitContext {
                Text(context)
                    .font(.caption)
                    .foregroundColor(.blue)
            }
            
            if let feedback = measurement.userFeedback {
                Text(feedback)
                    .font(.caption)
                    .foregroundColor(.gray)
            } else if measurement.ownsGarment {
                Button("Add fit feedback") {
                    showingFeedbackSheet = true
                }
                .font(.caption)
                .foregroundColor(.blue)
            }
        }
        .padding(.vertical, 4)
        .sheet(isPresented: $showingFeedbackSheet) {
            FeedbackSheet(measurement: measurement, isPresented: $showingFeedbackSheet)
        }
    }
}

#Preview {
    MeasurementDetailRow(measurement: BrandMeasurement(
        brand: "J.Crew",
        garmentName: "Cotton Sweater",
        measurementRange: MeasurementRange(min: 41, max: 43),
        size: "L",
        ownsGarment: true,
        fitContext: "Regular fit",
        userFeedback: nil,
        confidence: 0.9
    ))
    .padding()
} 
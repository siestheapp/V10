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
                Text(String(format: "%.1f\"", measurement.value))
            }
            
            if !measurement.fitType.isEmpty {
                Text(measurement.fitType)
                    .font(.caption)
                    .foregroundColor(.blue)
            }
            
            if !measurement.feedback.isEmpty {
                Text(measurement.feedback)
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
    MeasurementDetailRow(
        measurement: BrandMeasurement(
            brand: "J.Crew",
            garmentName: "Cotton Sweater",
            value: 42.0,
            size: "L",
            ownsGarment: true,
            fitType: "Regular fit",
            feedback: ""
        )
    )
    .padding()
} 
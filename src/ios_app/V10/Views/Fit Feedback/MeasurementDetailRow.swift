import SwiftUI

struct MeasurementDetailRow: View {
    let measurement: BrandMeasurement
    @State private var showingFeedbackSheet = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(measurement.brand)
                    .font(.headline)
                Spacer()
                if let range = measurement.chestRange {
                    Text(range)
                        .font(.title3)
                } else {
                    Text("\(measurement.value, specifier: "%.1f")\"")
                        .font(.title3)
                }
            }
            
            Text(measurement.garmentName)
                .foregroundColor(.gray)
            
            HStack {
                Text("Size \(measurement.size)")
                    .font(.subheadline)
                    .foregroundColor(.gray)
                
                Text("• Chest")
                    .font(.subheadline)
                    .foregroundColor(.gray)
            }
            
            if !measurement.fitType.isEmpty {
                Text(measurement.fitType)
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
        .padding(.vertical, 8)
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
            chestRange: "41.0-43.0",
            size: "L",
            ownsGarment: true,
            fitType: "Regular fit",
            feedback: ""
        )
    )
    .padding()
} 
import SwiftUI

struct DetailedMeasurementView: View {
    let measurement: IdealMeasurement
    @Binding var isPresented: Bool
    
    var body: some View {
        NavigationView {
            VStack(spacing: 24) {
                // Current value
                VStack(spacing: 8) {
                    Text("Current")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                    Text("\(measurement.value, specifier: "%.1f")\"")
                        .font(.system(size: 42, weight: .medium))
                        .foregroundColor(.blue)
                }
                .padding(.top)
                
                // All ranges
                VStack(spacing: 16) {
                    RangeSection(
                        label: "Ideal Range",
                        range: measurement.range.min...measurement.range.max,
                        color: .green
                    )
                    
                    RangeSection(
                        label: "Tight Fit",
                        range: (measurement.range.min - 1)...(measurement.range.min),
                        color: .orange
                    )
                    
                    RangeSection(
                        label: "Loose Fit",
                        range: measurement.range.max...(measurement.range.max + 1),
                        color: .orange
                    )
                    
                    RangeSection(
                        label: "Absolute Range",
                        range: (measurement.range.min - 2)...(measurement.range.max + 2),
                        color: .red
                    )
                }
                .padding()
                
                Spacer()
            }
            .navigationTitle(measurement.displayName)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") { isPresented = false }
                }
            }
        }
    }
}

struct RangeSection: View {
    let label: String
    let range: ClosedRange<Double>
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(label)
                .font(.headline)
            
            HStack {
                Text("\(range.lowerBound, specifier: "%.1f")\"")
                Spacer()
                Text("-")
                Spacer()
                Text("\(range.upperBound, specifier: "%.1f")\"")
            }
            .foregroundColor(.gray)
            
            Rectangle()
                .frame(height: 4)
                .foregroundColor(color)
                .cornerRadius(2)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
} 
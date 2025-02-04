import SwiftUI

struct GarmentDetailView: View {
    let garment: ClosetGarment
    @Binding var isPresented: Bool
    @State private var selectedMeasurement: String?
    
    var body: some View {
        NavigationView {
            List {
                Section(header: Text("GARMENT INFO")) {
                    LabeledContent("Brand", value: garment.brand)
                    LabeledContent("Name", value: garment.name)
                    LabeledContent("Size", value: garment.size)
                }
                
                Section(header: Text("MEASUREMENTS")) {
                    ForEach(Array(garment.measurements.keys.sorted()), id: \.self) { key in
                        if let range = garment.measurements[key] {
                            VStack(alignment: .leading) {
                                HStack {
                                    Text(key.capitalized)
                                        .font(.headline)
                                    Spacer()
                                    if range.min == range.max {
                                        Text(String(format: "%.1f\"", range.min))
                                    } else {
                                        Text(String(format: "%.1f-%.1f\"", range.min, range.max))
                                    }
                                }
                                
                                if let feedback = garment.feedback?[key] {
                                    Text(feedback)
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                } else {
                                    Button("Add feedback") {
                                        selectedMeasurement = key
                                    }
                                    .font(.caption)
                                    .foregroundColor(.blue)
                                }
                            }
                            .padding(.vertical, 4)
                        }
                    }
                }
            }
            .navigationTitle("Garment Details")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        isPresented = false
                    }
                }
            }
            .sheet(item: Binding(
                get: { selectedMeasurement.map { MeasurementIdentifier(name: $0) } },
                set: { selectedMeasurement = $0?.name }
            )) { identifier in
                FeedbackSheet(
                    measurement: BrandMeasurement(
                        brand: garment.brand,
                        garmentName: garment.name,
                        measurementRange: garment.measurements[identifier.name] ?? MeasurementRange(value: 0),
                        size: garment.size,
                        ownsGarment: garment.ownsGarment,
                        fitContext: nil,
                        userFeedback: garment.feedback?[identifier.name],
                        confidence: 0.9
                    ),
                    isPresented: Binding(
                        get: { selectedMeasurement != nil },
                        set: { if !$0 { selectedMeasurement = nil } }
                    )
                )
            }
        }
    }
}

// Helper to make String identifiable for sheet presentation
struct MeasurementIdentifier: Identifiable {
    let name: String
    var id: String { name }
}

#Preview {
    GarmentDetailView(
        garment: ClosetGarment(
            brand: "J.Crew",
            name: "Cotton Sweater",
            size: "L",
            measurements: [
                "chest": MeasurementRange(min: 41, max: 43),
                "sleeve": MeasurementRange(min: 34, max: 35)
            ],
            ownsGarment: true,
            feedback: ["chest": "Fits well in chest"]
        ),
        isPresented: .constant(true)
    )
} 
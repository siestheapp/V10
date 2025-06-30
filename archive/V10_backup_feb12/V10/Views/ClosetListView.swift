import SwiftUI

struct ClosetGarment: Identifiable {
    let id = UUID()
    let brand: String
    let name: String
    let size: String
    let measurements: [String: MeasurementRange]  // e.g. ["chest": MeasurementRange(41, 43)]
    let ownsGarment: Bool
    let feedback: [String: String]?  // Feedback for each measurement
}

struct ClosetListView: View {
    @State private var garments: [ClosetGarment] = []
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var selectedGarment: ClosetGarment?
    
    var body: some View {
        NavigationView {
            Group {
                if isLoading {
                    ProgressView("Loading your closet...")
                } else if let error = errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                } else {
                    List {
                        ForEach(garments) { garment in
                            GarmentRow(garment: garment)
                                .contentShape(Rectangle())
                                .onTapGesture {
                                    selectedGarment = garment
                                }
                        }
                    }
                }
            }
            .navigationTitle("My Closet")
            .sheet(item: $selectedGarment) { garment in
                GarmentDetailView(
                    garment: garment,
                    isPresented: Binding(
                        get: { selectedGarment != nil },
                        set: { if !$0 { selectedGarment = nil } }
                    )
                )
            }
            .onAppear {
                loadCloset()
            }
        }
    }
    
    private func loadCloset() {
        // TODO: Load from server
        // For now, add sample data
        self.garments = [
            ClosetGarment(
                brand: "J.Crew",
                name: "Cotton Sweater",
                size: "L",
                measurements: [
                    "chest": MeasurementRange(min: 41, max: 43),
                    "sleeve": MeasurementRange(min: 34, max: 35)
                ],
                ownsGarment: true,
                feedback: nil
            ),
            ClosetGarment(
                brand: "Theory",
                name: "Brenan Polo",
                size: "S",
                measurements: [
                    "chest": MeasurementRange(min: 36, max: 38),
                    "sleeve": MeasurementRange(min: 33.5, max: 34)
                ],
                ownsGarment: true,
                feedback: ["chest": "Tight fit, good for polo"]
            )
        ]
        isLoading = false
    }
}

struct GarmentRow: View {
    let garment: ClosetGarment
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(garment.brand)
                .font(.headline)
            Text(garment.name)
                .foregroundColor(.gray)
            HStack {
                Text(garment.size)
                    .font(.subheadline)
                if !garment.ownsGarment {
                    Text("(Tried on)")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
            }
        }
        .padding(.vertical, 4)
    }
}

// Update to use baseURL
let url = URL(string: "\(baseURL)/user/18/measurements") 
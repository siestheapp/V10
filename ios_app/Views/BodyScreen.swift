import SwiftUI

class BodyMeasurementViewModel: ObservableObject {
    @Published var estimatedChest: String = ""
    @Published var isLoading = false
    @Published var error: String?

    func fetchBodyMeasurements() {
        guard let url = URL(string: "http://localhost:5001/user/1/body-measurements") else { return }
        isLoading = true
        error = nil

        URLSession.shared.dataTask(with: url) { data, response, err in
            DispatchQueue.main.async {
                self.isLoading = false
                if let err = err {
                    self.error = err.localizedDescription
                    return
                }
                guard let data = data else {
                    self.error = "No data"
                    return
                }
                if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                   let chest = json["estimated_chest"] as? Double {
                    self.estimatedChest = String(format: "%.2f in", chest)
                } else {
                    self.error = "Could not parse measurement"
                }
            }
        }.resume()
    }
}

struct BodyScreen: View {
    @StateObject private var viewModel = BodyMeasurementViewModel()

    var body: some View {
        VStack(spacing: 24) {
            Text("Body Measurements")
                .font(.largeTitle)
                .bold()
            if viewModel.isLoading {
                ProgressView()
            } else if let error = viewModel.error {
                Text("Error: \(error)").foregroundColor(.red)
            } else if !viewModel.estimatedChest.isEmpty {
                Text("Estimated Chest: \(viewModel.estimatedChest)")
                    .font(.title2)
                    .padding()
            } else {
                Text("No measurement available.")
                    .foregroundColor(.gray)
            }
            Spacer()
        }
        .onAppear {
            viewModel.fetchBodyMeasurements()
        }
        .padding()
        .navigationTitle("Body")
    }
}

struct BodyScreen_Previews: PreviewProvider {
    static var previews: some View {
        BodyScreen()
    }
} 
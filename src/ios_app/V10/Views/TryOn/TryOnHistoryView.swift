import SwiftUI

struct TryOnHistoryView: View {
    @State private var tryOns: [TryOnHistoryItem] = []
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var selectedTryOn: TryOnHistoryItem?
    
    var body: some View {
        Group {
            if isLoading {
                loadingView
            } else if let error = errorMessage {
                errorView(error)
            } else if tryOns.isEmpty {
                emptyStateView
            } else {
                tryOnsList
            }
        }
        .onAppear {
            loadTryOnHistory()
        }
    }
    
    private var loadingView: some View {
        ProgressView("Loading try-ons...")
            .onAppear {
                print("🎯 TRY-ON HISTORY: Loading try-on sessions...")
            }
    }
    
    private func errorView(_ error: String) -> some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.largeTitle)
                .foregroundColor(.orange)
            Text("Could not load try-ons")
                .font(.headline)
            Text(error)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
            Button("Try Again") {
                loadTryOnHistory()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }
    
    private var emptyStateView: some View {
        VStack(spacing: 16) {
            Image(systemName: "tshirt")
                .font(.system(size: 60))
                .foregroundColor(.gray)
            Text("No Try-Ons Yet")
                .font(.title2)
                .fontWeight(.semibold)
            Text("Start a try-on session to track how different brands and sizes fit you!")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
        }
        .padding()
    }
    
    private var tryOnsList: some View {
        List(tryOns) { tryOn in
            TryOnHistoryRow(tryOn: tryOn)
                .contentShape(Rectangle())
                .onTapGesture {
                    selectedTryOn = tryOn
                }
        }
        .sheet(item: $selectedTryOn) { tryOn in
            TryOnDetailView(tryOn: tryOn)
        }
    }
    
    private func loadTryOnHistory() {
        guard let url = URL(string: "\(Config.baseURL)/user/\(Config.defaultUserId)/tryons") else {
            errorMessage = "Invalid URL"
            isLoading = false
            return
        }
        
        print("🎯 Loading try-on history from: \(url)")
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                
                if let error = error {
                    print("❌ Network error loading try-ons: \(error)")
                    errorMessage = "Network error: \(error.localizedDescription)"
                    return
                }
                
                guard let data = data else {
                    errorMessage = "No data received"
                    return
                }
                
                do {
                    let items = try JSONDecoder().decode([TryOnHistoryItem].self, from: data)
                    print("✅ Loaded \(items.count) try-on sessions")
                    tryOns = items
                } catch {
                    print("❌ Decoding error: \(error)")
                    errorMessage = "Could not load try-ons: \(error.localizedDescription)"
                }
            }
        }.resume()
    }
}

struct TryOnHistoryRow: View {
    let tryOn: TryOnHistoryItem
    
    var body: some View {
        HStack(spacing: 12) {
            // Product Image - LARGER for better identification
            AsyncImage(url: URL(string: tryOn.imageUrl ?? "")) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } placeholder: {
                Rectangle()
                    .fill(Color.gray.opacity(0.3))
                    .overlay(
                        Image(systemName: "tshirt")
                            .foregroundColor(.gray)
                            .font(.title2)
                    )
            }
            .frame(width: 80, height: 80)  // Increased from 60x60 to 80x80
            .clipShape(RoundedRectangle(cornerRadius: 12))
            
            // Product Info
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(tryOn.brand)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .textCase(.uppercase)
                    Spacer()
                    Text(tryOn.formattedDate)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                
                Text(tryOn.productName)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .lineLimit(2)
                
                HStack {
                    // Size Badge
                    let sizeText = tryOn.fitType != nil ? "Size \(tryOn.sizeTried) \(tryOn.fitType!)" : "Size \(tryOn.sizeTried)"
                    Text(sizeText)
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 2)
                        .background(Color.blue.opacity(0.1))
                        .foregroundColor(.blue)
                        .clipShape(Capsule())
                    
                    Spacer()
                    
                    // Feedback Badge
                    HStack(spacing: 4) {
                        Text(tryOn.feedbackEmoji)
                            .font(.caption)
                        Text(tryOn.overallFeedback)
                            .font(.caption)
                            .fontWeight(.medium)
                    }
                    .padding(.horizontal, 8)
                    .padding(.vertical, 2)
                    .background(tryOn.feedbackColor.opacity(0.1))
                    .foregroundColor(tryOn.feedbackColor)
                    .clipShape(Capsule())
                }
            }
            
            Spacer()
        }
        .padding(.vertical, 4)
    }
}

struct TryOnDetailView: View {
    let tryOn: TryOnHistoryItem
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Product Header
                    VStack(alignment: .leading, spacing: 12) {
                        AsyncImage(url: URL(string: tryOn.imageUrl ?? "")) { image in
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                        } placeholder: {
                            Rectangle()
                                .fill(Color.gray.opacity(0.3))
                                .aspectRatio(1, contentMode: .fit)
                                .overlay(
                                    Image(systemName: "tshirt")
                                        .font(.system(size: 40))
                                        .foregroundColor(.gray)
                                )
                        }
                        .frame(maxHeight: 200)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(tryOn.brand)
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .textCase(.uppercase)
                            
                            Text(tryOn.productName)
                                .font(.title2)
                                .fontWeight(.semibold)
                            
                            Text("Tried on \(tryOn.formattedDate)")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                        }
                    }
                    
                    // Size & Overall Feedback
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Fit Summary")
                            .font(.headline)
                        
                        HStack {
                            VStack(alignment: .leading) {
                                Text("Size Tried")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                let sizeAndFit = tryOn.fitType != nil ? "\(tryOn.sizeTried) \(tryOn.fitType!)" : tryOn.sizeTried
                                Text(sizeAndFit)
                                    .font(.title3)
                                    .fontWeight(.semibold)
                            }
                            
                            Spacer()
                            
                            VStack(alignment: .trailing) {
                                Text("Overall Fit")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                HStack {
                                    Text(tryOn.feedbackEmoji)
                                    Text(tryOn.overallFeedback)
                                        .font(.title3)
                                        .fontWeight(.semibold)
                                        .foregroundColor(tryOn.feedbackColor)
                                }
                            }
                        }
                        .padding()
                        .background(Color(.systemGray6))
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                    }
                    
                    // Detailed Feedback
                    if hasDetailedFeedback {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Detailed Feedback")
                                .font(.headline)
                            
                            VStack(spacing: 8) {
                                if let chest = tryOn.chestFeedback, !chest.isEmpty {
                                    feedbackRow(dimension: "Chest", feedback: chest)
                                }
                                if let waist = tryOn.waistFeedback, !waist.isEmpty {
                                    feedbackRow(dimension: "Waist", feedback: waist)
                                }
                                if let sleeve = tryOn.sleeveFeedback, !sleeve.isEmpty {
                                    feedbackRow(dimension: "Sleeve", feedback: sleeve)
                                }
                                if let neck = tryOn.neckFeedback, !neck.isEmpty {
                                    feedbackRow(dimension: "Neck", feedback: neck)
                                }
                            }
                        }
                    }
                    
                    // Measurements
                    if !tryOn.measurements.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Size Guide Measurements")
                                .font(.headline)
                            
                            VStack(spacing: 8) {
                                ForEach(Array(tryOn.measurements.keys.sorted()), id: \.self) { key in
                                    if let value = tryOn.measurements[key] {
                                        HStack {
                                            Text(key.capitalized)
                                                .font(.subheadline)
                                            Spacer()
                                            Text(value)
                                                .font(.subheadline)
                                                .fontWeight(.medium)
                                        }
                                        .padding(.horizontal)
                                        .padding(.vertical, 8)
                                        .background(Color(.systemGray6))
                                        .clipShape(RoundedRectangle(cornerRadius: 8))
                                    }
                                }
                            }
                        }
                    }
                    
                    Spacer()
                }
                .padding()
            }
            .navigationTitle("Try-On Details")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
    
    private var hasDetailedFeedback: Bool {
        return [tryOn.chestFeedback, tryOn.waistFeedback, tryOn.sleeveFeedback, tryOn.neckFeedback]
            .compactMap { $0 }
            .contains { !$0.isEmpty }
    }
    
    private func feedbackRow(dimension: String, feedback: String) -> some View {
        HStack {
            Text(dimension)
                .font(.subheadline)
            Spacer()
            Text(feedback)
                .font(.subheadline)
                .fontWeight(.medium)
                .foregroundColor(feedbackColor(for: feedback))
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }
    
    private func feedbackColor(for feedback: String) -> Color {
        switch feedback.lowercased() {
        case "good fit", "perfect":
            return .green
        case "tight but i like it", "loose but i like it":
            return .orange
        case "too tight", "too loose":
            return .red
        default:
            return .primary
        }
    }
}

#Preview {
    TryOnHistoryView()
}

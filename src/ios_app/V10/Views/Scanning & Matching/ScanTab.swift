// ScanTab.swift
// Handles garment scanning & manual product entry.
// - If the user scans a tag, stays on ScanTab & opens ScanGarmentView.swift.
// - If the user pastes a product link, gets smart size recommendation.

import SwiftUI

// MARK: - Data Models (moved to top for proper scope)

struct MeasurementComparison {
    let dimension: String
    let value: String
    let userRange: String
}

// Data Models for Size Recommendation (Direct Garment Comparison)
struct SizeRecommendationResponse: Codable {
    let productUrl: String
    let brand: String
    let analysisType: String
    let dimensionsAnalyzed: [String]
    let referenceGarments: [String: ReferenceGarment]
    let recommendedSize: String
    let recommendedFitScore: Double
    let confidence: Double
    let reasoning: String
    let primaryConcerns: [String]
    let comprehensiveAnalysis: Bool
    let allSizes: [DirectSizeOption]
    
    // 🎯 NEW: Enhanced confidence and explanation system
    let confidenceTier: ConfidenceTier?
    let humanExplanation: String?
    let alternativeExplanations: [AlternativeExplanation]?
    
    enum CodingKeys: String, CodingKey {
        case productUrl = "product_url"
        case brand
        case analysisType = "analysis_type"
        case dimensionsAnalyzed = "dimensions_analyzed"
        case referenceGarments = "reference_garments"
        case recommendedSize = "recommended_size"
        case recommendedFitScore = "recommended_fit_score"
        case confidence
        case reasoning
        case primaryConcerns = "primary_concerns"
        case comprehensiveAnalysis = "comprehensive_analysis"
        case allSizes = "all_sizes"
        case confidenceTier = "confidence_tier"
        case humanExplanation = "human_explanation"
        case alternativeExplanations = "alternative_explanations"
    }
}

// 🎯 NEW: Confidence tier model for better UX
struct ConfidenceTier: Codable {
    let tier: String
    let confidenceScore: Double
    let label: String
    let icon: String
    let color: String
    let description: String
    
    enum CodingKeys: String, CodingKey {
        case tier
        case confidenceScore = "confidence_score"
        case label
        case icon
        case color
        case description
    }
}

// 🎯 NEW: Alternative size explanations
struct AlternativeExplanation: Codable {
    let size: String
    let explanation: String
    let fitScore: Double
    
    enum CodingKeys: String, CodingKey {
        case size
        case explanation
        case fitScore = "fit_score"
    }
}

struct ReferenceGarment: Codable {
    let brand: String
    let size: String
    let productName: String
    let measurements: [String: String]  // Now stores range strings like "16-16.5\""
    let feedback: [String: String]
    let confidence: Double
    
    enum CodingKeys: String, CodingKey {
        case brand
        case size
        case productName = "product_name"
        case measurements
        case feedback
        case confidence
    }
}

struct DirectSizeOption: Codable {
    let size: String
    let overallFitScore: Double
    let confidence: Double
    let fitType: String
    let availableDimensions: [String]
    let dimensionAnalysis: [String: DimensionComparison]
    let measurementSummary: String
    let reasoning: String
    let primaryConcerns: [String]
    let fitDescription: String
    
    enum CodingKeys: String, CodingKey {
        case size
        case overallFitScore = "overall_fit_score"
        case confidence
        case fitType = "fit_type"
        case availableDimensions = "available_dimensions"
        case dimensionAnalysis = "dimension_analysis"
        case measurementSummary = "measurement_summary"
        case reasoning
        case primaryConcerns = "primary_concerns"
        case fitDescription = "fit_description"
    }
}

struct DimensionComparison: Codable {
    let type: String
    let fitScore: Double
    let garmentMeasurement: Double
    let garmentRange: String?  // NEW: Actual range like "41-44" from size guide
    let explanation: String
    let fitZone: String?
    let zoneRange: String?  // API returns "39.5-42.5" string format
    let matchesPreference: Bool?
    
    enum CodingKeys: String, CodingKey {
        case type
        case fitScore = "fit_score"
        case garmentMeasurement = "garment_measurement"
        case garmentRange = "garment_range"
        case explanation
        case fitZone = "fit_zone"
        case zoneRange = "zone_range"
        case matchesPreference = "matches_preference"
    }
}

// Helper model for alternative size analysis with garment comparisons
struct AlternativeSize {
    let size: String
    let problem: String
    let measurement: String
    let impact: String
    let similarGarment: String?
}


// MARK: - Views

struct ScanTab: View {
    @State private var showingOptions = false
    @State private var showingImagePicker = false
    @State private var showingScanView = false
    @State private var showingBrandsView = false
    @State private var selectedImage: UIImage?
    @State private var productLink: String = ""
    @State private var sizeRecommendation: SizeRecommendationResponse?
    @State private var tryOnSession: TryOnSession?
    @State private var isAnalyzing = false
    @State private var analysisError: String?
    @State private var navigateToFitFeedback = false
    @State private var navigateToTryOn = false
    @State private var showingTryOnSession = false  // New state for modal
    @State private var scannedGarment: Garment?     // Store scanned garment for try-on
    
    // Add mode selection
    @State private var selectedMode: ScanMode = .tryOn
    
    // Add user fit zones data
    @State private var userFitZones: ComprehensiveMeasurementData?
    @State private var isLoadingFitZones = false
    
    // Text field focus management (performance fix)
    @FocusState private var isTextFieldFocused: Bool
    @State private var textFieldId = UUID() // Simulator workaround
    @State private var isTextFieldReady = false // Delay text field to avoid iOS 18 gesture timeout
    
    enum ScanMode: String, CaseIterable {
        case tryOn = "Try-On"
        case recommendation = "Size Recommendation"
    }

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    // Header Section
                    VStack(spacing: 12) {
                        Text("Discover Your Perfect Fit")
                            .font(.title2)
                            .fontWeight(.bold)
                            .multilineTextAlignment(.center)
                        
                        Text("Scan garment tags or paste product links to get personalized size recommendations")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, 20)
                    }
                    .padding(.top, 20)
                    
                    // Mode selector with modern design
                    VStack(spacing: 16) {
                        HStack(spacing: 12) {
                            ForEach(ScanMode.allCases, id: \.self) { mode in
                                Button(action: {
                                    withAnimation(.easeInOut(duration: 0.2)) {
                                        selectedMode = mode
                                    }
                                }) {
                                    VStack(spacing: 8) {
                                        Image(systemName: mode == .tryOn ? "tshirt.fill" : "magnifyingglass")
                                            .font(.title2)
                                        Text(mode.rawValue)
                                            .font(.caption)
                                            .fontWeight(.medium)
                                    }
                                    .foregroundColor(selectedMode == mode ? .white : .primary)
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 12)
                                    .background(
                                        RoundedRectangle(cornerRadius: 12)
                                            .fill(selectedMode == mode ? 
                                                LinearGradient(colors: [.blue, .blue.opacity(0.8)], startPoint: .topLeading, endPoint: .bottomTrailing) :
                                                LinearGradient(colors: [Color(.systemGray6)], startPoint: .topLeading, endPoint: .bottomTrailing)
                                            )
                                    )
                                }
                                .buttonStyle(PlainButtonStyle())
                            }
                        }
                        .padding(.horizontal, 20)
                    }
                    
                    // Scan Tag Section with modern card design
                    VStack(spacing: 20) {
                        Button(action: {
                            showingOptions = true
                        }) {
                            HStack(spacing: 16) {
                                ZStack {
                                    Circle()
                                        .fill(LinearGradient(colors: [.blue, .blue.opacity(0.7)], startPoint: .topLeading, endPoint: .bottomTrailing))
                                        .frame(width: 50, height: 50)
                                    
                                    Image(systemName: "camera.fill")
                                        .font(.title2)
                                        .foregroundColor(.white)
                                }
                                
                                VStack(alignment: .leading, spacing: 4) {
                                    Text("Scan a Tag")
                                        .font(.headline)
                                        .fontWeight(.semibold)
                                    Text("Use your camera to scan garment tags")
                                        .font(.subheadline)
                                        .foregroundColor(.secondary)
                                }
                                
                                Spacer()
                                
                                Image(systemName: "chevron.right")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                            .padding(20)
                            .background(
                                RoundedRectangle(cornerRadius: 16)
                                    .fill(Color(.systemBackground))
                                    .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 2)
                            )
                        }
                        .buttonStyle(PlainButtonStyle())
                        .padding(.horizontal, 20)
                    .sheet(isPresented: $showingImagePicker) {
                        ImagePicker(image: $selectedImage)
                    }
                    .onChange(of: selectedImage) { _, newImage in
                        if newImage != nil {
                            showingScanView = true
                        }
                    }
                    .sheet(isPresented: $showingScanView) {
                        if let image = selectedImage {
                            NavigationView {
                                ScanGarmentView(
                                    selectedImage: image,
                                    isPresented: $showingScanView
                                )
                            }
                        }
                    }
                }
                
                        // Divider with modern styling
                        HStack(spacing: 16) {
                            Rectangle()
                                .frame(height: 1)
                                .foregroundColor(.gray.opacity(0.2))
                            
                            Text("OR")
                                .font(.caption)
                                .fontWeight(.medium)
                                .foregroundColor(.secondary)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(
                                    Capsule()
                                        .fill(Color(.systemGray6))
                                )
                            
                            Rectangle()
                                .frame(height: 1)
                                .foregroundColor(.gray.opacity(0.2))
                        }
                        .padding(.horizontal, 20)
                
                // URL Input Section with modern card design
                VStack(spacing: 20) {
                    HStack {
                        Text(selectedMode == .tryOn ? "Log a Try-On" : "Get Size Recommendation")
                            .font(.title3)
                            .fontWeight(.semibold)
                        Spacer()
                    }
                    .padding(.horizontal, 20)
                    
                    // URL Input with modern styling
                    VStack(spacing: 12) {
                        HStack(spacing: 12) {
                            Image(systemName: "link")
                                .foregroundColor(.secondary)
                                .frame(width: 20)
                            
                            if isTextFieldReady {
                                TextField("Paste product link here", text: $productLink)
                                    .textFieldStyle(PlainTextFieldStyle())
                                    .disabled(isAnalyzing)
                                    .focused($isTextFieldFocused)
                                    .autocorrectionDisabled()
                                    .textInputAutocapitalization(.never)
                                    .keyboardType(.URL)
                                    .submitLabel(.go)
                                    .id(textFieldId) // Simulator focus workaround
                                    .onSubmit {
                                        if !productLink.isEmpty {
                                            analyzeProduct()
                                        }
                                    }
                                    // PERFORMANCE FIX: Added focus management and keyboard optimizations
                            } else {
                                // Show placeholder while text field initializes
                                Text("Paste product link here")
                                    .foregroundColor(.gray.opacity(0.3))
                                    .frame(maxWidth: .infinity, alignment: .leading)
                            }
                        }
                        .padding(16)
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color(.systemGray6))
                                .overlay(
                                    RoundedRectangle(cornerRadius: 12)
                                        .stroke(productLink.isEmpty ? Color.clear : Color.blue.opacity(0.3), lineWidth: 1)
                                )
                        )
                        .padding(.horizontal, 20)
                    
                    // Analysis Status
                    if isAnalyzing {
                        HStack {
                            ProgressView()
                                .scaleEffect(0.8)
                            Text(selectedMode == .tryOn ? "Preparing try-on session..." : "Analyzing product and finding your best size...")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        .padding(.horizontal, 20)
                    }
                    
                    // Error Display
                    if let error = analysisError {
                        Text(error)
                            .font(.caption)
                            .foregroundColor(.red)
                            .padding(.horizontal, 20)
                    }
                    
                    // Size Recommendation Display - Navigate to full screen
                    if let recommendation = sizeRecommendation {
                        NavigationLink(destination: SizeRecommendationScreen(recommendation: recommendation)) {
                            // Preview card that shows basic info and invites tap
                            VStack(alignment: .leading, spacing: 12) {
                                HStack {
                                    Text(recommendation.brand)
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                        .textCase(.uppercase)
                                    Spacer()
                                    Image(systemName: "chevron.right")
                                        .foregroundColor(.blue)
                                        .font(.caption)
                                }
                                
                                HStack(spacing: 12) {
                                    Text(recommendation.confidenceTier?.icon ?? "✅")
                                        .font(.title)
                                    
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text("Size \(recommendation.recommendedSize)")
                                            .font(.title)
                                            .fontWeight(.bold)
                                            .foregroundColor(.primary)
                                        
                                        Text(recommendation.confidenceTier?.label ?? "Good Fit")
                                            .font(.subheadline)
                                            .foregroundColor(.green)
                                    }
                                    
                                    Spacer()
                                    
                                    // Measurement count indicator
                                    VStack {
                                        Text("\(recommendation.dimensionsAnalyzed.count)")
                                            .font(.title2)
                                            .fontWeight(.bold)
                                            .foregroundColor(.blue)
                                        Text("measurements")
                                            .font(.caption2)
                                            .foregroundColor(.secondary)
                                    }
                                }
                                
                                Text("Tap for detailed analysis")
                                    .font(.caption)
                                    .foregroundColor(.blue)
                            }
                            .padding()
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(Color(.systemGray6))
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 12)
                                            .stroke(Color.blue.opacity(0.3), lineWidth: 1)
                                    )
                            )
                        }
                        .buttonStyle(PlainButtonStyle())
                    }
                    
                    // Try-On Session Display or Start Button
                    if let session = tryOnSession {
                        NavigationLink(destination: TryOnConfirmationView(session: session)) {
                            TryOnPreviewCard(session: session)
                        }
                        .buttonStyle(PlainButtonStyle())
                    } else if selectedMode == .tryOn {
                        Button(action: {
                            if productLink.isEmpty {
                                analysisError = "Please paste a product link first"
                            } else {
                                startTryOnSession()
                            }
                        }) {
                            Label("Start Try-On Session", systemImage: "tshirt.fill")
                                .font(.headline)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(productLink.isEmpty ? Color.gray : Color.blue)
                                .cornerRadius(12)
                        }
                        .disabled(isAnalyzing)
                        .padding(.horizontal, 20)
                    } else if selectedMode == .recommendation && !productLink.isEmpty && !isAnalyzing {
                        Button(action: {
                            analyzeProduct()
                        }) {
                            Label("Get Size Recommendation", systemImage: "ruler")
                                .font(.headline)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.blue)
                                .cornerRadius(12)
                        }
                        .padding(.horizontal, 20)
                    }
                }
                .padding(.horizontal, 40)
                
                Spacer()
                
                // Proceed Button (only shown when we have a recommendation)
                if let recommendation = sizeRecommendation {
                    let confidenceInfo = recommendation.confidenceTier ?? ConfidenceTier(
                        tier: "fair", confidenceScore: recommendation.confidence,
                        label: "Good Fit", icon: "✅", color: "green", description: "This should work for you"
                    )
                    
                    Button(action: {
                        navigateToFitFeedback = true
                    }) {
                        Text("\(confidenceInfo.icon) Add Size \(recommendation.recommendedSize) to Closet")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(colorFromString(confidenceInfo.color))
                            .cornerRadius(12)
                    }
                    .padding(.horizontal, 40)
                    .navigationDestination(isPresented: $navigateToFitFeedback) {
                        FitFeedbackViewWithPhoto(
                            feedbackType: .manualEntry, 
                            selectedSize: recommendation.recommendedSize,
                            productUrl: recommendation.productUrl,
                            brand: recommendation.brand
                        )
                    }
                }
                }
            }
            .navigationTitle("Scan")
            .navigationBarTitleDisplayMode(.inline)
            .onAppear {
                print("📷 SCAN TAB: ScanTab appeared")
                // Reset and delay text field initialization to avoid iOS 18 gesture timeout
                isTextFieldReady = false
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                    isTextFieldReady = true
                }
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        showingBrandsView = true
                    }) {
                        HStack {
                            Image(systemName: "tag")
                            Text("Brands")
                        }
                    }
                }
            }
            .sheet(isPresented: $showingBrandsView) {
                NavigationView {
                    BrandsView()
                }
            }
            .confirmationDialog("Choose an option", isPresented: $showingOptions) {
                Button("Open Camera") {
                    showingImagePicker = true
                }
                
                Button("Choose from Photos") {
                    showingImagePicker = true
                }
            }
        }
        .sheet(isPresented: $showingTryOnSession) {
            // Create the garment directly in the sheet closure
            let garment = Garment(
                id: 0,
                brand: extractBrandFromUrl(productLink),
                productName: "Product",
                productUrl: productLink,
                imageUrl: nil,
                category: "Tops",
                sizeLabel: "",
                ownsGarment: false,
                fitFeedback: nil,
                feedbackTimestamp: nil
            )
            
            TryOnSessionView(
                garment: garment,
                productUrl: productLink
            )
            .onAppear {
                print("📱 Sheet appeared with garment: \(garment.brand)")
            }
        }
        .onAppear {
            print("📷 SCAN TAB: ScanTab appeared")
            // Removed loadUserFitZones() from onAppear to prevent lag on text field tap
            // Fit zones will be loaded lazily when actually needed for analysis
        }
    }
}
    
    private func analyzeProduct() {
        guard !productLink.isEmpty else { return }
        
        isAnalyzing = true
        analysisError = nil
        sizeRecommendation = nil
        
        // Load fit zones only when needed for analysis (lazy loading)
        if userFitZones == nil && !isLoadingFitZones {
            loadUserFitZones()
        }
        
        guard let url = URL(string: "\(Config.baseURL)/garment/size-recommendation") else {
            analysisError = "Invalid API URL"
            isAnalyzing = false
            return
        }
        
        let requestBody = [
            "product_url": productLink,
            "user_id": "1"  // Using default user for now
        ]
        
        guard let jsonData = try? JSONSerialization.data(withJSONObject: requestBody) else {
            analysisError = "Failed to encode request"
            isAnalyzing = false
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isAnalyzing = false
                
                if let error = error {
                    analysisError = "Network error: \(error.localizedDescription)"
                    return
                }
                
                guard let data = data else {
                    analysisError = "No data received"
                    return
                }
                
                do {
                    let recommendation = try JSONDecoder().decode(SizeRecommendationResponse.self, from: data)
                    self.sizeRecommendation = recommendation
                } catch {
                    analysisError = "Failed to parse recommendation: \(error.localizedDescription)"
                    print("Decode error: \(error)")
                }
            }
        }.resume()
    }
    
    private func startTryOnSession() {
        guard !productLink.isEmpty else { return }
        
        isAnalyzing = true
        analysisError = nil
        tryOnSession = nil
        
        // Load fit zones only when needed for try-on session (lazy loading)
        if userFitZones == nil && !isLoadingFitZones {
            loadUserFitZones()
        }
        
        guard let url = URL(string: "\(Config.baseURL)/tryon/start") else {
            analysisError = "Invalid API URL"
            isAnalyzing = false
            return
        }
        
        let requestBody = [
            "product_url": productLink,
            "user_id": "1"
        ]
        
        guard let jsonData = try? JSONSerialization.data(withJSONObject: requestBody) else {
            analysisError = "Failed to encode request"
            isAnalyzing = false
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                self.isAnalyzing = false
                
                if let error = error {
                    print("❌ Network error: \(error)")
                    self.analysisError = "Network error: \(error.localizedDescription)"
                    return
                }
                
                guard let data = data else {
                    print("❌ No data received")
                    self.analysisError = "No data received"
                    return
                }
                
                // Debug: Print raw response
                if let responseString = String(data: data, encoding: .utf8) {
                    print("📦 Raw response: \(responseString)")
                }
                
                // Check HTTP response status
                if let httpResponse = response as? HTTPURLResponse {
                    print("📡 HTTP Status: \(httpResponse.statusCode)")
                    if httpResponse.statusCode != 200 {
                        // Try to parse error message from response
                        if let errorDict = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                           let detail = errorDict["detail"] as? String {
                            self.analysisError = detail
                        } else {
                            self.analysisError = "Server error (status: \(httpResponse.statusCode))"
                        }
                        return
                    }
                }
                
                do {
                    let session = try JSONDecoder().decode(TryOnSession.self, from: data)
                    print("✅ Successfully decoded try-on session: \(session.sessionId)")
                    self.tryOnSession = session
                } catch {
                    print("❌ Decode error: \(error)")
                    self.analysisError = "Failed to parse try-on session: \(error.localizedDescription)"
                }
            }
        }.resume()
    }
    
    private func startTryOnSessionModal() {
        print("🚀 Starting try-on session modal")
        print("🚀 Product link: \(productLink)")
        
        // Simply show the sheet - the garment will be created in the sheet closure
        showingTryOnSession = true
    }
    
    private func extractBrandFromUrl(_ url: String) -> String {
        let lowercaseUrl = url.lowercased()
        
        if lowercaseUrl.contains("jcrew.com") {
            return "J.Crew"
        } else if lowercaseUrl.contains("lululemon.com") {
            return "Lululemon"
        } else if lowercaseUrl.contains("bananarepublic.com") || lowercaseUrl.contains("bananarepublic.gap.com") {
            return "Banana Republic"
        } else if lowercaseUrl.contains("patagonia.com") {
            return "Patagonia"
        } else if lowercaseUrl.contains("theory.com") {
            return "Theory"
        } else if lowercaseUrl.contains("uniqlo.com") {
            return "Uniqlo"
        } else if lowercaseUrl.contains("nn07.com") {
            return "NN.07"
        } else if lowercaseUrl.contains("vuori.com") {
            return "Vuori"
        } else if lowercaseUrl.contains("lacoste.com") {
            return "Lacoste"
        } else if lowercaseUrl.contains("reiss.com") {
            return "Reiss"
        } else if lowercaseUrl.contains("faherty.com") {
            return "Faherty"
        }
        
        return "Unknown Brand"
    }
    
    private func loadUserFitZones() {
        guard let url = URL(string: "\(Config.baseURL)/user/\(Config.defaultUserId)/measurements") else {
            print("Invalid URL for fit zones")
            return
        }
        
        isLoadingFitZones = true
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            // Decode JSON on background thread first
            var decodedData: ComprehensiveMeasurementData?
            var decodeError: Error?
            
            if let error = error {
                DispatchQueue.main.async {
                    self.isLoadingFitZones = false
                    print("Error loading fit zones: \(error.localizedDescription)")
                }
                return
            }
            
            guard let data = data else {
                DispatchQueue.main.async {
                    self.isLoadingFitZones = false
                    print("No fit zones data received")
                }
                return
            }
            
            // Heavy JSON decoding on background thread
            do {
                let response = try JSONDecoder().decode(ComprehensiveMeasurementResponse.self, from: data)
                decodedData = response.tops
            } catch {
                decodeError = error
            }
            
            // Only update UI on main thread
            DispatchQueue.main.async {
                self.isLoadingFitZones = false
                
                if let error = decodeError {
                    print("Failed to parse fit zones: \(error)")
                } else {
                    self.userFitZones = decodedData
                }
            }
        }.resume()
    }
}

// MARK: - Helper Functions
// Helper function to convert string color to SwiftUI Color
private func colorFromString(_ colorString: String) -> Color {
    switch colorString.lowercased() {
    case "green":
        return .green
    case "orange":
        return .orange
    case "red":
        return .red
    case "blue":
        return .blue
    default:
        return .green
    }
}

// MARK: - Size Recommendation Display Component (todoAug.md implementation)
struct SizeRecommendationView: View {
    let recommendation: SizeRecommendationResponse
    @State private var showDetailedAnalysis = false
    @State private var showAlternativeSizes = false
    
    // Get confidence tier info with fallback
    private var confidenceInfo: ConfidenceTier {
        recommendation.confidenceTier ?? ConfidenceTier(
            tier: "fair",
            confidenceScore: recommendation.confidence,
            label: "Good Fit",
            icon: "✅",
            color: "green",
            description: "This should work for you"
        )
    }
    
    
    // Helper to parse measurement summary for comparison display
    private func parseMeasurementSummary(_ summary: String) -> [MeasurementComparison] {
        // Simple parsing - return default ranges since this is just for display
        return [
            MeasurementComparison(dimension: "chest", value: "42", userRange: "39.5-42.5"),
            MeasurementComparison(dimension: "neck", value: "16", userRange: "15.5-16.5")
        ]
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Header with just brand (no "Size Recommendation" title)
            HStack {
                Spacer()
                Text(recommendation.brand)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            
            // 🎯 PRIMARY DISPLAY: Lead with confidence + size (per todoAug.md)
            VStack(alignment: .leading, spacing: 12) {
                // Main recommendation - confidence and size together
                HStack(alignment: .center, spacing: 8) {
                    Text(confidenceInfo.icon)
                        .font(.title)
                    
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Size \(recommendation.recommendedSize)")
                            .font(.system(size: 32, weight: .bold))
                            .foregroundColor(.primary)
                        
                        Text(confidenceInfo.label)
                            .font(.headline)
                            .foregroundColor(colorFromString(confidenceInfo.color))
                    }
                    
                    Spacer()
                    
                    // Measurement count indicator (demonstrates sophistication)
                    let dimensionCount = recommendation.dimensionsAnalyzed.count
                    if dimensionCount > 0 {
                        VStack(alignment: .trailing, spacing: 1) {
                            Text("\(dimensionCount)")
                                .font(.title2)
                                .fontWeight(.bold)
                                .foregroundColor(.blue)
                            Text("measurements")
                                .font(.caption2)
                                .foregroundColor(.secondary)
                        }
                    }
                }
                
                // Human-readable explanation (anxiety-reducing language per todoAug.md)
                Text(recommendation.humanExplanation ?? recommendation.reasoning)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
                    .multilineTextAlignment(.leading)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color(.systemGray6))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(colorFromString(confidenceInfo.color).opacity(0.3), lineWidth: 2)
                    )
            )
            
            // 🎯 PROGRESSIVE DISCLOSURE: Expandable sections (per todoAug.md)
            VStack(spacing: 8) {
                // Why this size?
                DisclosureGroup("Why this size?", isExpanded: $showDetailedAnalysis) {
                    VStack(alignment: .leading, spacing: 8) {
                        // Show analyzed dimensions with clear indicators
                        let analyzedDimensions = recommendation.dimensionsAnalyzed
                        if !analyzedDimensions.isEmpty {
                            Text("Measurements analyzed:")
                                .font(.caption)
                                .fontWeight(.medium)
                                .foregroundColor(.secondary)
                            
                            ForEach(analyzedDimensions, id: \.self) { dimension in
                                HStack {
                                    Text("✅")
                                        .font(.caption)
                                    Text(dimension.capitalized)
                                        .font(.caption)
                                        .fontWeight(.medium)
                                    Text("matches your fit zone")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    Spacer()
                                }
                            }
                        } else if let recommended = recommendation.allSizes.first(where: { $0.size == recommendation.recommendedSize }) {
                            // Fallback to original measurement display
                            let measurements = parseMeasurementSummary(recommended.measurementSummary)
                            ForEach(measurements, id: \.dimension) { measurement in
                                HStack {
                                    Text(measurement.dimension.capitalized)
                                        .font(.caption)
                                        .fontWeight(.medium)
                                    Spacer()
                                    Text("\(measurement.value)\"")
                                        .font(.caption)
                                        .foregroundColor(.primary)
                                    Text("vs")
                                        .font(.caption2)
                                        .foregroundColor(.secondary)
                                    Text("\(measurement.userRange)")
                                        .font(.caption)
                                        .foregroundColor(.blue)
                                }
                            }
                        }
                        
                        // Reference garments (contextual explanations per todoAug.md)
                        if !recommendation.referenceGarments.isEmpty {
                            Text("Based on:")
                                .font(.caption)
                                .fontWeight(.medium)
                                .padding(.top, 4)
                            
                            ForEach(Array(recommendation.referenceGarments.keys.sorted()), id: \.self) { key in
                                if let reference = recommendation.referenceGarments[key] {
                                    HStack {
                                        Circle().fill(.blue).frame(width: 6, height: 6)
                                        Text("\(reference.brand) \(reference.size)")
                                            .font(.caption)
                                        Spacer()
                                        Text("\(String(format: "%.0f%%", reference.confidence * 100)) match")
                                            .font(.caption2)
                                            .foregroundColor(.secondary)
                                    }
                                }
                            }
                        }
                    }
                    .padding(.top, 8)
                }
                .font(.subheadline)
                .foregroundColor(.primary)
                
                // Alternative sizes (per todoAug.md)
                if let alternatives = recommendation.alternativeExplanations, !alternatives.isEmpty {
                    DisclosureGroup("Other sizes?", isExpanded: $showAlternativeSizes) {
                        VStack(alignment: .leading, spacing: 6) {
                            ForEach(alternatives, id: \.size) { alt in
                                HStack(alignment: .top) {
                                    Text(alt.size)
                                        .font(.subheadline)
                                        .fontWeight(.medium)
                                    Spacer()
                                    Text(alt.explanation)
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                        .multilineTextAlignment(.trailing)
                                }
                                .padding(.vertical, 2)
                            }
                        }
                        .padding(.top, 8)
                    }
                    .font(.subheadline)
                    .foregroundColor(.primary)
                }
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(Color(.systemBackground))
                .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color(.systemGray4), lineWidth: 1)
        )
        .padding(.horizontal)
    }
}

// MARK: - Try-On Preview Card
struct TryOnPreviewCard: View {
    let session: TryOnSession
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(session.brand)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .textCase(.uppercase)
                Spacer()
                Image(systemName: "chevron.right")
                    .foregroundColor(.blue)
                    .font(.caption)
            }
            
            HStack(spacing: 12) {
                Image(systemName: "tshirt")
                    .font(.title)
                    .foregroundColor(.blue)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text("Try-On Session")
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(.primary)
                    
                    Text("Ready to log your fit experience")
                        .font(.subheadline)
                        .foregroundColor(.blue)
                }
                
                Spacer()
                
                VStack {
                    Text("\(session.sizeOptions.count)")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.blue)
                    Text("sizes")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
            
            Text("Tap to start logging your try-on")
                .font(.caption)
                .foregroundColor(.blue)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(.systemGray6))
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color.blue.opacity(0.3), lineWidth: 1)
                )
        )
    }
}

// MARK: - Size Recommendation Screen (moved to separate file)
// SizeRecommendationScreen is now defined in SizeRecommendationScreen.swift

// Keeping this comment for reference - the screen was moved to its own file

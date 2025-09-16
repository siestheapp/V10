// OptimizedScanTab.swift
// Performance-optimized version with no UI lag
// Fixes: text input delay, heavy main thread operations, inefficient data loading

import SwiftUI

struct OptimizedScanTab: View {
    // MARK: - State Properties
    @State private var selectedImage: UIImage?
    @State private var showingImagePicker = false
    @State private var showingScanView = false
    @State private var productLink = ""
    @State private var isAnalyzing = false
    @State private var analysisError: String?
    @State private var sizeRecommendation: SizeRecommendationResponse?
    @State private var tryOnSession: TryOnSession?
    @State private var selectedMode: AnalysisMode = .recommendation
    
    // Performance optimization: Lazy load fit zones only when needed
    @State private var userFitZones: ComprehensiveMeasurementData?
    @State private var isLoadingFitZones = false
    @State private var fitZonesLoadTask: Task<Void, Never>?
    
    // Text field focus management
    @FocusState private var isTextFieldFocused: Bool
    
    // Simulator workaround
    @State private var textFieldId = UUID()
    
    enum AnalysisMode {
        case recommendation
        case tryOn
    }
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Header
                    headerSection
                    
                    // Mode Selector
                    modeSelector
                    
                    // Scan Tag Section
                    scanTagSection
                    
                    // Divider
                    dividerSection
                    
                    // URL Input Section - OPTIMIZED
                    urlInputSection
                    
                    // Results Section
                    resultsSection
                }
                .padding(.vertical, 20)
            }
            .navigationTitle("Find Your Fit")
            .navigationBarTitleDisplayMode(.large)
            .background(Color(.systemGroupedBackground))
        }
        .onDisappear {
            // Cancel any pending fit zone loading
            fitZonesLoadTask?.cancel()
        }
    }
    
    // MARK: - View Components
    
    private var headerSection: some View {
        VStack(spacing: 8) {
            Text("Get Your Perfect Size")
                .font(.title2)
                .fontWeight(.bold)
            Text("Scan a tag or paste a product link")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .padding(.horizontal, 20)
    }
    
    private var modeSelector: some View {
        Picker("Mode", selection: $selectedMode) {
            Text("Size Recommendation").tag(AnalysisMode.recommendation)
            Text("Try-On Session").tag(AnalysisMode.tryOn)
        }
        .pickerStyle(SegmentedPickerStyle())
        .padding(.horizontal, 20)
    }
    
    private var scanTagSection: some View {
        Button(action: { showingImagePicker = true }) {
            HStack(spacing: 16) {
                ZStack {
                    Circle()
                        .fill(LinearGradient(
                            colors: [.blue, .blue.opacity(0.7)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ))
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
    
    private var dividerSection: some View {
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
    }
    
    private var urlInputSection: some View {
        VStack(spacing: 20) {
            HStack {
                Text(selectedMode == .tryOn ? "Log a Try-On" : "Get Size Recommendation")
                    .font(.title3)
                    .fontWeight(.semibold)
                Spacer()
            }
            .padding(.horizontal, 20)
            
            // OPTIMIZED: Text field with no lag
            VStack(spacing: 12) {
                HStack(spacing: 12) {
                    Image(systemName: "link")
                        .foregroundColor(.secondary)
                        .frame(width: 20)
                    
                    // PERFORMANCE FIX: Removed onTapGesture that was loading data
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
                                performAnalysis()
                            }
                        }
                }
                .padding(16)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color(.systemGray6))
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(
                                    isTextFieldFocused ? Color.blue.opacity(0.5) :
                                    productLink.isEmpty ? Color.clear :
                                    Color.blue.opacity(0.3),
                                    lineWidth: 1
                                )
                        )
                )
                .animation(.easeInOut(duration: 0.2), value: isTextFieldFocused)
                .padding(.horizontal, 20)
                
                // Status indicators
                if isAnalyzing {
                    HStack {
                        ProgressView()
                            .scaleEffect(0.8)
                        Text(selectedMode == .tryOn ?
                             "Preparing try-on session..." :
                             "Analyzing product and finding your best size...")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding(.horizontal, 20)
                }
                
                if let error = analysisError {
                    Text(error)
                        .font(.caption)
                        .foregroundColor(.red)
                        .padding(.horizontal, 20)
                }
            }
            
            // Action button
            if !productLink.isEmpty && !isAnalyzing {
                Button(action: performAnalysis) {
                    Label(
                        selectedMode == .tryOn ? "Start Try-On Session" : "Get Size Recommendation",
                        systemImage: selectedMode == .tryOn ? "tshirt.fill" : "ruler"
                    )
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
    }
    
    private var resultsSection: some View {
        VStack(spacing: 16) {
            // Size Recommendation Display
            if let recommendation = sizeRecommendation {
                NavigationLink(destination: SizeRecommendationScreen(recommendation: recommendation)) {
                    recommendationCard(recommendation)
                }
                .buttonStyle(PlainButtonStyle())
            }
            
            // Try-On Session Display
            if let session = tryOnSession {
                NavigationLink(destination: TryOnConfirmationView(session: session)) {
                    OptimizedTryOnPreviewCard(session: session)
                }
                .buttonStyle(PlainButtonStyle())
            }
        }
    }
    
    private func recommendationCard(_ recommendation: SizeRecommendationResponse) -> some View {
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
        .padding(.horizontal, 20)
    }
    
    // MARK: - Optimized Network Functions
    
    private func performAnalysis() {
        if selectedMode == .tryOn {
            startOptimizedTryOnSession()
        } else {
            analyzeProductOptimized()
        }
    }
    
    private func analyzeProductOptimized() {
        guard !productLink.isEmpty else { return }
        
        isAnalyzing = true
        analysisError = nil
        sizeRecommendation = nil
        
        Task {
            do {
                let url = URL(string: "\(Config.baseURL)/analyze/comprehensive")!
                let requestBody = ["product_url": productLink, "user_id": "1"]
                let jsonData = try JSONSerialization.data(withJSONObject: requestBody)
                
                let recommendation = try await OptimizedNetworkManager.shared.fetch(
                    SizeRecommendationResponse.self,
                    from: url,
                    method: "POST",
                    body: jsonData,
                    useCache: false  // Don't cache POST requests
                )
                
                await MainActor.run {
                    self.sizeRecommendation = recommendation
                    self.isAnalyzing = false
                }
            } catch {
                await MainActor.run {
                    self.analysisError = "Failed to analyze: \(error.localizedDescription)"
                    self.isAnalyzing = false
                }
            }
        }
    }
    
    private func startOptimizedTryOnSession() {
        guard !productLink.isEmpty else { return }
        
        isAnalyzing = true
        analysisError = nil
        tryOnSession = nil
        
        // Load fit zones asynchronously only when needed
        if userFitZones == nil && !isLoadingFitZones {
            loadFitZonesAsync()
        }
        
        Task {
            do {
                let url = URL(string: "\(Config.baseURL)/tryon/start")!
                let requestBody = ["product_url": productLink, "user_id": "1"]
                let jsonData = try JSONSerialization.data(withJSONObject: requestBody)
                
                // Create request
                var request = URLRequest(url: url)
                request.httpMethod = "POST"
                request.setValue("application/json", forHTTPHeaderField: "Content-Type")
                request.httpBody = jsonData
                
                let (data, response) = try await URLSession.shared.data(for: request)
                
                guard let httpResponse = response as? HTTPURLResponse else {
                    throw URLError(.badServerResponse)
                }
                
                if httpResponse.statusCode != 200 {
                    if let errorData = try? JSONDecoder().decode(ErrorResponse.self, from: data) {
                        throw NSError(domain: "", code: httpResponse.statusCode,
                                    userInfo: [NSLocalizedDescriptionKey: errorData.detail])
                    }
                    throw URLError(.badServerResponse)
                }
                
                let session = try JSONDecoder().decode(TryOnSession.self, from: data)
                
                await MainActor.run {
                    self.tryOnSession = session
                    self.isAnalyzing = false
                }
            } catch {
                await MainActor.run {
                    self.analysisError = "Failed to start try-on: \(error.localizedDescription)"
                    self.isAnalyzing = false
                }
            }
        }
    }
    
    private func loadFitZonesAsync() {
        guard fitZonesLoadTask == nil else { return }
        
        isLoadingFitZones = true
        
        fitZonesLoadTask = Task {
            do {
                let url = URL(string: "\(Config.baseURL)/user/\(Config.defaultUserId)/measurements")!
                
                let data = try await OptimizedNetworkManager.shared.fetch(
                    ComprehensiveMeasurementResponse.self,
                    from: url,
                    useCache: true  // Use cache for fit zones
                )
                
                await MainActor.run {
                    self.userFitZones = data.tops
                    self.isLoadingFitZones = false
                }
            } catch {
                await MainActor.run {
                    print("Failed to load fit zones: \(error)")
                    self.isLoadingFitZones = false
                }
            }
            
            fitZonesLoadTask = nil
        }
    }
}

// MARK: - Supporting Views

struct OptimizedTryOnPreviewCard: View {
    let session: TryOnSession
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Try-On Session Ready")
                    .font(.headline)
                Spacer()
                Image(systemName: "chevron.right")
                    .foregroundColor(.blue)
            }
            
            Text(session.brand)
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            Text(session.productName)
                .font(.body)
            
            HStack {
                if !session.sizeOptions.isEmpty {
                    Label("\(session.sizeOptions.count) sizes available", systemImage: "ruler")
                        .font(.caption)
                        .foregroundColor(.blue)
                }
                Spacer()
                Text("Tap to continue")
                    .font(.caption)
                    .foregroundColor(.blue)
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(.systemGray6))
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color.green.opacity(0.3), lineWidth: 1)
                )
        )
        .padding(.horizontal, 20)
    }
}

// Error response model
struct ErrorResponse: Codable {
    let detail: String
}

// TryOnConfirmationView.swift
// Handles try-on session confirmation and size selection before feedback.
// Replaces the deleted ProductConfirmationView for TryOnSession flow.

import SwiftUI

// J.Crew-style fit description modifier (matching their exact CSS)
struct JCrewFitDescriptionStyle: ViewModifier {
    let isSelected: Bool
    let fitType: String
    
    func body(content: Content) -> some View {
        HStack(spacing: 12) {
            // J.Crew official fit type image
            AsyncImage(url: URL(string: "https://www.jcrew.com/next-static/images/fit-types/SHIRTS_FIT_\(fitType).png")) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fit)
            } placeholder: {
                // Fallback icon if image doesn't load
                Image(systemName: "tshirt")
                    .foregroundColor(.gray)
            }
            .frame(width: 40, height: 40)
            
            // Description text
            content
                .font(.system(size: 13, weight: .regular)) // .8125rem = 13px
                .foregroundColor(Color.black) // #000
                .kerning(0.3) // letter-spacing: .3px
                .lineSpacing(13 * 0.4) // line-height: 1.4
                .multilineTextAlignment(.leading) // justify-content: left
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding(8) // .5rem = 8px
        .background(
            RoundedRectangle(cornerRadius: 5) // border-radius: 5px
                .fill(Color(red: 245/255, green: 245/255, blue: 245/255, opacity: 0.502)) // rgba(245,245,245,.5019607843)
                .overlay(
                    RoundedRectangle(cornerRadius: 5)
                        .stroke(Color(red: 190/255, green: 190/255, blue: 190/255), lineWidth: 1) // 1px solid #bebebe
                )
        )
    }
}

struct TryOnConfirmationView: View {
    let session: TryOnSession
    @State private var selectedSize: String = ""
    @State private var selectedFit: String = ""
    @State private var navigateToFeedback = false
    @State private var displayedProductName: String = ""
    @Environment(\.presentationMode) var presentationMode
    
    // Get fit options from session data
    private var availableFitOptions: [String] {
        return session.fitOptions.isEmpty ? [] : session.fitOptions
    }
    
    
    // Computed property to determine if Continue button should be disabled
    private var isDisabled: Bool {
        var requirements: [Bool] = [!selectedSize.isEmpty]
        
        if !availableFitOptions.isEmpty {
            requirements.append(!selectedFit.isEmpty)
        }
        
        
        return !requirements.allSatisfy { $0 }
    }
    
    var body: some View {
        NavigationView {
            ScrollView {
            VStack(spacing: 20) {
                // Product Image - LARGE like real ecommerce apps
                if !session.productImage.isEmpty {
                    AsyncImage(url: URL(string: session.productImage)) { image in
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                    } placeholder: {
                        Rectangle()
                            .fill(Color.gray.opacity(0.1))
                            .aspectRatio(1, contentMode: .fit) // Square placeholder
                            .overlay(
                                ProgressView()
                            )
                    }
                    // Full width, let image determine its own height
                    .frame(maxWidth: .infinity)
                    // No fixed height - image maintains its natural aspect ratio
                    // No background color - removes grey padding
                }
                
                VStack(spacing: 20) {
                    // Product Info (compact, below image)
                    VStack(spacing: 6) {
                        Text(session.brand)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .textCase(.uppercase)
                            .tracking(1.2)
                        
                        Text(displayedProductName.isEmpty ? session.productName : displayedProductName)
                            .font(.title3)
                            .fontWeight(.semibold)
                            .multilineTextAlignment(.center)
                    }
                    .padding(.horizontal)
                
                // Fit Selection (for products with fit options)
                if !availableFitOptions.isEmpty {
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Select Fit Type")
                            .font(.headline)
                            .fontWeight(.bold)
                        
                        Text("Which fit are you trying on? This affects the measurements.")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        
                        VStack(spacing: 16) {
                            // Fit option buttons
                            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 3), spacing: 12) {
                                ForEach(availableFitOptions, id: \.self) { fit in
                                    Button(action: {
                                        print("🔍 Fit button tapped: '\(fit)'")
                                        selectedFit = fit
                                        print("🔍 Selected fit is now: '\(selectedFit)'")
                                        
                                    }) {
                                        Text(fit)
                                            .font(.subheadline)
                                            .fontWeight(.medium)
                                            .foregroundColor(selectedFit == fit ? .white : .primary)
                                            .frame(maxWidth: .infinity)
                                            .padding(.vertical, 12)
                                            .padding(.horizontal, 8)
                                            .background(
                                                RoundedRectangle(cornerRadius: 8)
                                                    .fill(selectedFit == fit ? Color.blue : Color(.systemGray5))
                                            )
                                    }
                                }
                            }
                            
                            // J.Crew-style fit description with official images (shows only for selected fit)
                            if !selectedFit.isEmpty {
                                if selectedFit == "Tall" {
                                    Text("2\" longer in the body and sleeves compared to our Classic fit.")
                                        .modifier(JCrewFitDescriptionStyle(isSelected: true, fitType: "Tall"))
                                } else if selectedFit == "Slim" {
                                    Text("Tapered fit through the body and sleeves.")
                                        .modifier(JCrewFitDescriptionStyle(isSelected: true, fitType: "Slim"))
                                } else if selectedFit == "Classic" {
                                    Text("Our signature fit with a comfortable, time-tested cut.")
                                        .modifier(JCrewFitDescriptionStyle(isSelected: true, fitType: "Classic"))
                                } else if selectedFit == "Relaxed" {
                                    Text("Roomier fit through the body for added comfort.")
                                        .modifier(JCrewFitDescriptionStyle(isSelected: true, fitType: "Relaxed"))
                                }
                            }
                        }
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color(.systemBackground))
                            .shadow(color: .black.opacity(0.1), radius: 2, x: 0, y: 1)
                    )
                }
                
                
                // Size Selection - Dressing Room Experience
                VStack(alignment: .leading, spacing: 16) {
                    Text("What Size Are You Trying On?")
                        .font(.headline)
                        .fontWeight(.bold)
                    
                    Text("Select the size on the tag you're about to try on")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    
                    LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 3), spacing: 12) {
                        ForEach(session.sizeOptions, id: \.self) { size in
                            Button(action: {
                                print("🔍 Size button tapped: '\(size)'")
                                selectedSize = size
                                print("🔍 Selected size is now: '\(selectedSize)'")
                            }) {
                                Text(size)
                                    .font(.headline)
                                    .foregroundColor(selectedSize == size ? .white : .primary)
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(
                                        RoundedRectangle(cornerRadius: 8)
                                            .fill(selectedSize == size ? Color.blue : Color(.systemGray5))
                                    )
                            }
                        }
                    }
                }
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color(.systemBackground))
                        .shadow(color: .black.opacity(0.1), radius: 2, x: 0, y: 1)
                )
                
                // Continue Button - At bottom for better UX flow
                Button(action: {
                    print("🔍 Continue button tapped")
                    print("🔍 Selected size: '\(selectedSize)'")
                    print("🔍 Selected fit: '\(selectedFit)'")
                    print("🔍 Is J.Crew: \(session.brand.lowercased() == "j.crew")")
                    navigateToFeedback = true
                }) {
                    Text("Continue")
                        .font(.headline)
                        .fontWeight(.semibold)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(isDisabled ? Color.gray : Color.blue)
                        )
                }
                .disabled(isDisabled)
                .padding(.horizontal)
                .padding(.bottom, 20)
                .onAppear {
                    print("🔍 Continue button appeared - selectedSize: '\(selectedSize)', selectedFit: '\(selectedFit)', disabled: \(isDisabled)")
                }
                
                }  // End of inner VStack
            }
            .padding()
        }
        .navigationTitle("Confirm Try-On")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $navigateToFeedback) {
            NavigationView {
                FitFeedbackViewWithPhoto(
                    feedbackType: .manualEntry,
                    selectedSize: selectedSize,
                    productUrl: session.productUrl,
                    brand: session.brand,
                    fitType: selectedFit.isEmpty ? nil : selectedFit,
                    selectedColor: nil,
                    availableMeasurements: session.availableMeasurements
                )
            }
            }
            .navigationTitle("Try-On")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Try Another") {
                        presentationMode.wrappedValue.dismiss()
                    }
                }
            }
        }
        .onAppear {
            print("🔍 TryOnConfirmationView appeared")
            print("🔍 Session size options: \(session.sizeOptions)")
            print("🔍 Session fit options: \(session.fitOptions)")
            print("🔍 Available fit options: \(availableFitOptions)")
            print("🔍 Fit options count: \(availableFitOptions.count)")
            
            // Initialize displayed values from session
            // Use base product name (without fit prefix) like J.Crew app
            displayedProductName = session.baseProductName ?? session.productName
            
            // Always default to Classic fit like J.Crew app
            selectedFit = "Classic"
            print("🔍 Default to Classic fit (J.Crew standard behavior)")
            
            print("🔍 Available measurements: \(session.availableMeasurements)")
            print("🔍 Selected size: '\(selectedSize)'")
            
            // Debug each fit option
            for (index, fit) in availableFitOptions.enumerated() {
                print("🔍 Fit option [\(index)]: '\(fit)'")
            }
            
            // Auto-select first size if only one option
            if session.sizeOptions.count == 1 {
                selectedSize = session.sizeOptions.first ?? ""
                print("🔍 Auto-selected size: '\(selectedSize)'")
            }
            
        }
    }
    
}


//#Preview {
//    NavigationView {
//        TryOnConfirmationView(session: TryOnSession(
//            sessionId: "test-123",
//            brand: "J.Crew",
//            brandId: 1,
//            productName: "Vintage-wash cotton pocket T-shirt",
//            productUrl: "https://example.com/shirt",
//            productImage: "",
//            availableMeasurements: ["Chest", "Neck", "Sleeve"],
//            feedbackOptions: [],
//            sizeOptions: ["S", "M", "L", "XL"],
//            fitOptions: ["Classic", "Slim", "Tall"],
//            colorOptions: [],
//            currentColor: "",
//            nextStep: "Try on the garment and provide feedback on how it fits."
//        ))
//    }
//}

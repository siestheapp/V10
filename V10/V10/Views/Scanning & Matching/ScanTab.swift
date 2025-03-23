// ScanTab.swift
// Handles garment scanning & manual product entry.
// - If the user scans a tag, stays on ScanTab & opens ScanGarmentView.swift.
// - If the user pastes a product link & selects a size, navigates to FitFeedbackView.swift.

import SwiftUI

struct ScanTab: View {
    @State private var showingOptions = false
    @State private var showingImagePicker = false
    @State private var showingScanView = false
    @State private var showingBrandsView = false
    @State private var selectedImage: UIImage?
    @State private var productLink: String = ""
    @State private var selectedSizeCategory: String = "Men's Tops"
    @State private var selectedSize: String? = nil
    @State private var navigateToFitFeedback = false
    @State private var navigateToScanGarment = false

    let sizeCategories = ["Men's Tops", "Men's Bottoms", "Women's Tops", "Women's Bottoms", "Unisex", "Shoes"]
    let sizeOptions = ["XS", "S", "M", "L", "XL", "XXL"]

    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                
                // Title
                Text("Scan")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                // Scan Button
                Button(action: {
                    showingOptions = true
                }) {
                    Text("Scan a Tag")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(10)
                }
                .padding(.horizontal, 40)

                // OR Divider
                HStack {
                    Rectangle()
                        .frame(height: 1)
                        .foregroundColor(.gray)
                    Text("OR")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                    Rectangle()
                        .frame(height: 1)
                        .foregroundColor(.gray)
                }
                .padding(.horizontal, 40)
                
                // Find by Link
                VStack(alignment: .leading, spacing: 10) {
                    Text("Find by Link")
                        .font(.headline)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    TextField("Paste product link here", text: $productLink)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .padding(.horizontal, 20)
                    
                    // Show size category dropdown only when link is entered
                    if !productLink.isEmpty {
                        Text("Select Size Category")
                            .font(.headline)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.top, 10)

                        Picker("Size Category", selection: $selectedSizeCategory) {
                            ForEach(sizeCategories, id: \.self) { category in
                                Text(category).tag(category)
                            }
                        }
                        .pickerStyle(MenuPickerStyle())
                        .padding(.horizontal, 20)
                        
                        Text("Select Size")
                            .font(.headline)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.top, 10)

                        Picker("Size", selection: $selectedSize) {
                            ForEach(sizeOptions, id: \.self) { size in
                                Text(size).tag(size as String?)
                            }
                        }
                        .pickerStyle(SegmentedPickerStyle())
                        .padding(.horizontal, 20)
                    }
                }
                .padding(.horizontal, 40)
                
                // Find Garment Button
                Button(action: {
                    navigateToFitFeedback = true
                }) {
                    Text("Find Garment")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(productLink.isEmpty || selectedSize == nil ? Color.gray : Color.blue)
                        .cornerRadius(10)
                }
                .padding(.horizontal, 40)
                .disabled(productLink.isEmpty || selectedSize == nil)
                .background(
                    NavigationLink(
                        destination: FitFeedbackView(feedbackType: .manualEntry, selectedSize: selectedSize ?? ""),
                        isActive: $navigateToFitFeedback
                    ) { EmptyView() }
                )
            }
            .padding(.top, 30)
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
                        .navigationTitle("Brands")
                        .toolbar {
                            ToolbarItem(placement: .navigationBarTrailing) {
                                Button("Done") {
                                    showingBrandsView = false
                                }
                            }
                        }
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
            .sheet(isPresented: $showingImagePicker) {
                ImagePicker(image: $selectedImage)
            }
            .onChange(of: selectedImage) { newImage in
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
    }
}

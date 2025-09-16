// GarmentPhotosView.swift
// Displays photos associated with a garment

import SwiftUI

struct GarmentPhotosView: View {
    let garmentId: Int
    @State private var photos: [GarmentPhoto] = []
    @State private var isLoading = true
    @State private var selectedPhoto: GarmentPhoto?
    @State private var showFullScreen = false
    @State private var showDeleteAlert = false
    @State private var photoToDelete: GarmentPhoto?
    
    var body: some View {
        ScrollView {
            if isLoading {
                ProgressView("Loading photos...")
                    .padding()
            } else if photos.isEmpty {
                VStack(spacing: 20) {
                    Image(systemName: "photo.on.rectangle.angled")
                        .font(.system(size: 60))
                        .foregroundColor(.gray)
                    Text("No photos yet")
                        .font(.headline)
                        .foregroundColor(.gray)
                    Text("Add photos during your next try-on session")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding()
                .frame(maxWidth: .infinity, minHeight: 200)
            } else {
                LazyVGrid(columns: [GridItem(.adaptive(minimum: 150))], spacing: 15) {
                    ForEach(photos) { photo in
                        PhotoThumbnail(photo: photo) {
                            selectedPhoto = photo
                            showFullScreen = true
                        } onDelete: {
                            photoToDelete = photo
                            showDeleteAlert = true
                        }
                    }
                }
                .padding()
            }
        }
        .navigationTitle("Try-On Photos")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            loadPhotos()
        }
        .sheet(isPresented: $showFullScreen) {
            if let photo = selectedPhoto {
                PhotoDetailView(photo: photo)
            }
        }
        .alert("Delete Photo", isPresented: $showDeleteAlert) {
            Button("Cancel", role: .cancel) {}
            Button("Delete", role: .destructive) {
                if let photo = photoToDelete {
                    deletePhoto(photo)
                }
            }
        } message: {
            Text("Are you sure you want to delete this photo?")
        }
    }
    
    private func loadPhotos() {
        guard let url = URL(string: "\(Config.baseURL)/garment/\(garmentId)/photos") else {
            isLoading = false
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                
                if let data = data,
                   let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                   let photosArray = json["photos"] as? [[String: Any]] {
                    
                    self.photos = photosArray.compactMap { dict in
                        guard let id = dict["id"] as? Int,
                              let photoUrl = dict["photo_url"] as? String else { return nil }
                        
                        return GarmentPhoto(
                            id: id,
                            photoUrl: photoUrl,
                            photoType: dict["photo_type"] as? String ?? "camera",
                            caption: dict["caption"] as? String ?? "",
                            metadata: dict["metadata"] as? [String: Any],
                            isPrimary: dict["is_primary"] as? Bool ?? false,
                            createdAt: dict["created_at"] as? String ?? ""
                        )
                    }
                }
            }
        }.resume()
    }
    
    private func deletePhoto(_ photo: GarmentPhoto) {
        guard let url = URL(string: "\(Config.baseURL)/photo/\(photo.id)") else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        
        URLSession.shared.dataTask(with: request) { _, _, _ in
            DispatchQueue.main.async {
                photos.removeAll { $0.id == photo.id }
            }
        }.resume()
    }
}

struct PhotoThumbnail: View {
    let photo: GarmentPhoto
    let onTap: () -> Void
    let onDelete: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            AsyncImage(url: URL(string: photo.photoUrl)) { image in
                image
                    .resizable()
                    .scaledToFill()
                    .frame(width: 150, height: 150)
                    .clipped()
                    .cornerRadius(10)
            } placeholder: {
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.gray.opacity(0.2))
                    .frame(width: 150, height: 150)
                    .overlay(
                        ProgressView()
                    )
            }
            .onTapGesture {
                onTap()
            }
            
            if photo.isPrimary {
                HStack {
                    Image(systemName: "star.fill")
                        .foregroundColor(.yellow)
                        .font(.caption)
                    Text("Primary")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            if !photo.caption.isEmpty {
                Text(photo.caption)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
            }
            
            HStack {
                Text(formatDate(photo.createdAt))
                    .font(.caption2)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Button(action: onDelete) {
                    Image(systemName: "trash")
                        .font(.caption)
                        .foregroundColor(.red)
                }
            }
        }
        .frame(width: 150)
    }
    
    private func formatDate(_ dateString: String) -> String {
        // Parse ISO date and format nicely
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
        
        if let date = formatter.date(from: String(dateString.prefix(19))) {
            formatter.dateStyle = .short
            formatter.timeStyle = .none
            return formatter.string(from: date)
        }
        
        return ""
    }
}

struct PhotoDetailView: View {
    let photo: GarmentPhoto
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            VStack {
                AsyncImage(url: URL(string: photo.photoUrl)) { image in
                    image
                        .resizable()
                        .scaledToFit()
                } placeholder: {
                    ProgressView()
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                }
                
                if !photo.caption.isEmpty {
                    Text(photo.caption)
                        .padding()
                        .background(Color(UIColor.systemGray6))
                        .cornerRadius(10)
                        .padding()
                }
                
                // Show metadata if available
                if let metadata = photo.metadata {
                    VStack(alignment: .leading, spacing: 8) {
                        if let size = metadata["size"] as? String {
                            Label("Size: \(size)", systemImage: "ruler")
                        }
                        if let fitType = metadata["fit_type"] as? String, !fitType.isEmpty {
                            Label("Fit: \(fitType)", systemImage: "aspectratio")
                        }
                        if let color = metadata["color"] as? String, !color.isEmpty {
                            Label("Color: \(color)", systemImage: "paintpalette")
                        }
                    }
                    .font(.caption)
                    .padding()
                    .background(Color(UIColor.systemGray6))
                    .cornerRadius(10)
                    .padding(.horizontal)
                }
                
                Spacer()
            }
            .navigationTitle("Photo Details")
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
}

// Model for garment photos
struct GarmentPhoto: Identifiable {
    let id: Int
    let photoUrl: String
    let photoType: String
    let caption: String
    let metadata: [String: Any]?
    let isPrimary: Bool
    let createdAt: String
}

import SwiftUI
import Combine

// MARK: - Image Cache Manager
final class ImageCacheManager {
    static let shared = ImageCacheManager()
    
    private let cache = NSCache<NSString, UIImage>()
    private let fileManager = FileManager.default
    private let diskCacheURL: URL
    
    private init() {
        cache.countLimit = 100 // Max 100 images in memory
        cache.totalCostLimit = 100 * 1024 * 1024 // Max 100MB in memory
        
        // Setup disk cache directory
        let cacheDirectory = fileManager.urls(for: .cachesDirectory, in: .userDomainMask).first!
        diskCacheURL = cacheDirectory.appendingPathComponent("ImageCache")
        
        // Create directory if needed
        try? fileManager.createDirectory(at: diskCacheURL, withIntermediateDirectories: true)
        
        // Clean old cache on init
        cleanOldCache()
    }
    
    func image(for url: URL) -> UIImage? {
        let key = url.absoluteString as NSString
        
        // Check memory cache
        if let cachedImage = cache.object(forKey: key) {
            return cachedImage
        }
        
        // Check disk cache
        let diskPath = diskCacheURL.appendingPathComponent(url.lastPathComponent)
        if let diskImage = UIImage(contentsOfFile: diskPath.path) {
            // Store in memory cache for faster access
            cache.setObject(diskImage, forKey: key, cost: diskImage.pngData()?.count ?? 0)
            return diskImage
        }
        
        return nil
    }
    
    func store(_ image: UIImage, for url: URL) {
        let key = url.absoluteString as NSString
        
        // Store in memory cache
        cache.setObject(image, forKey: key, cost: image.pngData()?.count ?? 0)
        
        // Store on disk asynchronously
        DispatchQueue.global(qos: .background).async { [weak self] in
            guard let self = self,
                  let data = image.jpegData(compressionQuality: 0.8) else { return }
            
            let diskPath = self.diskCacheURL.appendingPathComponent(url.lastPathComponent)
            try? data.write(to: diskPath)
        }
    }
    
    private func cleanOldCache() {
        DispatchQueue.global(qos: .background).async { [weak self] in
            guard let self = self else { return }
            
            let oneWeekAgo = Date().addingTimeInterval(-7 * 24 * 60 * 60)
            
            guard let files = try? self.fileManager.contentsOfDirectory(
                at: self.diskCacheURL,
                includingPropertiesForKeys: [.contentModificationDateKey],
                options: .skipsHiddenFiles
            ) else { return }
            
            for file in files {
                if let attributes = try? file.resourceValues(forKeys: [.contentModificationDateKey]),
                   let modificationDate = attributes.contentModificationDate,
                   modificationDate < oneWeekAgo {
                    try? self.fileManager.removeItem(at: file)
                }
            }
        }
    }
    
    func clearCache() {
        cache.removeAllObjects()
        try? fileManager.removeItem(at: diskCacheURL)
        try? fileManager.createDirectory(at: diskCacheURL, withIntermediateDirectories: true)
    }
}

// MARK: - Cached Async Image View
struct CachedAsyncImage<Content: View, Placeholder: View>: View {
    let url: URL?
    let content: (Image) -> Content
    let placeholder: () -> Placeholder
    
    @State private var image: UIImage?
    @State private var isLoading = false
    
    init(
        url: URL?,
        @ViewBuilder content: @escaping (Image) -> Content,
        @ViewBuilder placeholder: @escaping () -> Placeholder
    ) {
        self.url = url
        self.content = content
        self.placeholder = placeholder
    }
    
    var body: some View {
        Group {
            if let image = image {
                content(Image(uiImage: image))
            } else {
                placeholder()
                    .onAppear { loadImage() }
            }
        }
    }
    
    private func loadImage() {
        guard let url = url, !isLoading else { return }
        
        // Check cache first
        if let cachedImage = ImageCacheManager.shared.image(for: url) {
            self.image = cachedImage
            return
        }
        
        // Download image
        isLoading = true
        
        URLSession.shared.dataTask(with: url) { data, _, error in
            DispatchQueue.main.async {
                self.isLoading = false
                
                guard error == nil,
                      let data = data,
                      let downloadedImage = UIImage(data: data) else {
                    return
                }
                
                // Store in cache
                ImageCacheManager.shared.store(downloadedImage, for: url)
                
                // Update UI with animation
                withAnimation(.easeInOut(duration: 0.2)) {
                    self.image = downloadedImage
                }
            }
        }.resume()
    }
}

// MARK: - Convenience Init for CachedAsyncImage
extension CachedAsyncImage where Placeholder == ProgressView<EmptyView, EmptyView> {
    init(url: URL?, @ViewBuilder content: @escaping (Image) -> Content) {
        self.init(url: url, content: content, placeholder: { ProgressView() })
    }
}

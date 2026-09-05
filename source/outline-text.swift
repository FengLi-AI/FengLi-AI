import Foundation
import CoreText
import CoreGraphics

let configURL = URL(fileURLWithPath: CommandLine.arguments[1])
let jobs = try JSONSerialization.jsonObject(with: Data(contentsOf: configURL)) as! [[String: Any]]
var output: [[String: Any]] = []
func f(_ x: CGFloat) -> String { String(format: "%.3f", Double(x)) }
for job in jobs {
    let file = job["font"] as! String
    let descriptors = CTFontManagerCreateFontDescriptorsFromURL(URL(fileURLWithPath: file) as CFURL) as! [CTFontDescriptor]
    let font = CTFontCreateWithFontDescriptor(descriptors[0], CGFloat(job["size"] as! Double), nil)
    let text = job["text"] as! String
    let attr = NSAttributedString(string: text, attributes: [NSAttributedString.Key(kCTFontAttributeName as String): font])
    let line = CTLineCreateWithAttributedString(attr)
    let path = CGMutablePath()
    for run in CTLineGetGlyphRuns(line) as! [CTRun] {
        let count = CTRunGetGlyphCount(run)
        var glyphs = [CGGlyph](repeating: 0, count: count)
        var positions = [CGPoint](repeating: .zero, count: count)
        CTRunGetGlyphs(run, CFRange(location: 0, length: 0), &glyphs)
        CTRunGetPositions(run, CFRange(location: 0, length: 0), &positions)
        let runFont = (CTRunGetAttributes(run) as NSDictionary)[kCTFontAttributeName] as! CTFont
        for i in 0..<count {
            if let glyph = CTFontCreatePathForGlyph(runFont, glyphs[i], nil) {
                path.addPath(glyph, transform: CGAffineTransform(translationX: positions[i].x, y: positions[i].y))
            }
        }
    }
    let bounds = path.boundingBoxOfPath
    var tr = CGAffineTransform(a: 1, b: 0, c: 0, d: -1, tx: -bounds.minX, ty: bounds.maxY)
    let flipped = path.copy(using: &tr)!
    var d = ""
    flipped.applyWithBlock { p in
        let e = p.pointee
        switch e.type {
        case .moveToPoint: d += "M\(f(e.points[0].x)) \(f(e.points[0].y))"
        case .addLineToPoint: d += "L\(f(e.points[0].x)) \(f(e.points[0].y))"
        case .addQuadCurveToPoint: d += "Q\(f(e.points[0].x)) \(f(e.points[0].y)) \(f(e.points[1].x)) \(f(e.points[1].y))"
        case .addCurveToPoint: d += "C\(f(e.points[0].x)) \(f(e.points[0].y)) \(f(e.points[1].x)) \(f(e.points[1].y)) \(f(e.points[2].x)) \(f(e.points[2].y))"
        case .closeSubpath: d += "Z"
        @unknown default: break
        }
    }
    output.append(["text": text, "d": d, "width": bounds.width, "height": bounds.height, "advance": CTLineGetTypographicBounds(line, nil, nil, nil), "font": CTFontCopyPostScriptName(font)])
}
let data = try JSONSerialization.data(withJSONObject: output, options: [.sortedKeys])
FileHandle.standardOutput.write(data)

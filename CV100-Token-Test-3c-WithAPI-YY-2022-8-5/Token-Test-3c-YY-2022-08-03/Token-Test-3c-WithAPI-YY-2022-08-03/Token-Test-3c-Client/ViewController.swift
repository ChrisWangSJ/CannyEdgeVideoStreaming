/* ------------------------------------------------------------------------------------------------------*
* Company Name : CTI One Corporation                                                                     *
* Program name : ViewController.swift (Testing)                                                          *
* Coded By     : ZW                                                                                      *
* Date         : 2022-07-22                                                                              *
* Updated By   : YY                                                                                      *
* Date         : 2022-08-02                                                                              *
* Version      : v1.0.1                                                                                  *
* Copyright    : Copyright (c) 2022 CTI One Corporation                                                  *
* Purpose      : CV100_Token_Testing_3c                                                                  *
*              : Integrate TT2a. Shows a original video and processed video side by side                 *
*              : v1.0.0 2022-07-22 ZW Create                                                             *
*              : v1.0.1 2022-08-02 YY Add autoreleasepool to release NSImage objects                     *
---------------------------------------------------------------------------------------------------------*/


import Cocoa
import AVFoundation
import Token_Test_3c_Client_API

class ViewController: NSViewController {
    private var cameraManager: CameraManagerProtocol!
        
    @IBOutlet weak var originalNSImageView: NSImageView!
    @IBOutlet weak var resultNSImageView: NSImageView!
    // var resultNSImage : NSImage!
    // var originalNSImage : NSImage!
    let processingManager = ProcessingManager()
    var timer = Timer()
    // var recvFlag = 0

    override func viewDidLoad() {
        super.viewDidLoad()
        do {
          cameraManager = try CameraManager(containerView: originalNSImageView)
          cameraManager.delegate = self
        } catch {
          // Cath the error here
          print(error.localizedDescription)
        }
        // Start video steaming processing
        self.start()

        self.timer = Timer.scheduledTimer(withTimeInterval: 0.001, repeats: true, block: { [self] _ in
            self.processImage()
        
        })
        
    }

    override var representedObject: Any? {
        didSet {
        // Update the view, if already loaded.
        }
    }
  
  override func viewDidAppear() {
    super.viewDidAppear()
    do {
      try cameraManager.startSession()
    } catch {
      // Cath the error here
      print(error.localizedDescription)
    }
  }
  
  override func viewDidDisappear() {
    super.viewDidDisappear()
    do {
      try cameraManager.stopSession()
    } catch {
      // Cath the error here
      print(error.localizedDescription)
    }
  }
    func processImage(){
        /*
        if originalNSImage != nil{
            processingManager.setImage(image: originalNSImage)
        } else{
            return
        }
        */
        
        self.resultNSImageView.image = processingManager.getResultImage()
            
    }
    func start(){
          
        let server = "127.0.0.1"      // "localhost" caused the connection error once
        let port = UInt16("8801")!
        processingManager.start(server: server, port: port)
              
    }
}

extension ViewController: CameraManagerDelegate {
  func cameraManager(_ output: CameraCaptureOutput, didOutput sampleBuffer: CameraSampleBuffer, from connection: CameraCaptureConnection) {
 
      // 2022-08-02 YY Add autoreleasepool[] to release NSImage objects
      autoreleasepool{
          guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else
          {
              return
          }
          let originalCIImage = CIImage(cvImageBuffer: pixelBuffer)
          let originalCIContext = CIContext(options: nil)
          let imageWidth = CVPixelBufferGetWidth(pixelBuffer)
          let imageHeight = CVPixelBufferGetHeight(pixelBuffer)

          guard let originalCGImage = originalCIContext.createCGImage(originalCIImage, from: CGRect(x: 0, y: 0, width: imageWidth, height: imageHeight)) else{
              //print("originalCGImage nil", Date())
              return
          }
          let originalNSImage = NSImage(cgImage: originalCGImage, size: CGSize(width: imageWidth, height: imageHeight))
          processingManager.setImage(image: originalNSImage)
      }
  }
}





/* ------------------------------------------------------------------------------------------------------*
* Company Name : CTI One Corporation                                                                     *
* Program name : CameraManager.swift (Testing)                                                           *
* Coded By     : ZW                                                                                      *
* Date         : 2022-06-19                                                                              *
* Updated By   :                                                                                         *
* Date         :                                                                                         *
* Version      : v1.0.0                                                                                  *
* Copyright    : Copyright (c) 2022 CTI One Corporation                                                  *
* Purpose      : Handle Webcam                                                                           *
*              : v1.0.0 2022-06-19 ZW Create                                                             *
*              : v1.0.1 2022-08-03 YY Select eGlass as the first priority device                         *
---------------------------------------------------------------------------------------------------------*/

import AVFoundation

import Cocoa

public enum CameraError: LocalizedError {
  case cannotDetectCameraDevice
  case cannotAddInput
  case previewLayerConnectionError
  case cannotAddOutput
  case videoSessionNil
  
  public var localizedDescription: String {
    switch self {
    case .cannotDetectCameraDevice: return "Cannot detect camera device"
    case .cannotAddInput: return "Cannot add camera input"
    case .previewLayerConnectionError: return "Preview layer connection error"
    case .cannotAddOutput: return "Cannot add video output"
    case .videoSessionNil: return "Camera video session is nil"
    }
  }
}

public typealias CameraCaptureOutput = AVCaptureOutput
public typealias CameraSampleBuffer = CMSampleBuffer
public typealias CameraCaptureConnection = AVCaptureConnection

public protocol CameraManagerDelegate: AnyObject {
  func cameraManager(_ output: CameraCaptureOutput, didOutput sampleBuffer: CameraSampleBuffer, from connection: CameraCaptureConnection)
}

public protocol CameraManagerProtocol: AnyObject {
  var delegate: CameraManagerDelegate? { get set }
  
  func startSession() throws
  func stopSession() throws
}

public final class CameraManager: NSObject, CameraManagerProtocol {
  
  private var previewLayer: AVCaptureVideoPreviewLayer!
  private var videoSession: AVCaptureSession!
  private var cameraDevice: AVCaptureDevice!
  
  private let cameraQueue: DispatchQueue
  
  private let containerView: NSView
  
  public weak var delegate: CameraManagerDelegate?
  
  public init(containerView: NSView) throws {
    self.containerView = containerView
    cameraQueue = DispatchQueue(label: "sample buffer delegate", attributes: [])
    
    super.init()
    
    try prepareCamera()
  }
  
    deinit {
    previewLayer = nil
    videoSession = nil
    cameraDevice = nil
  }
  
  private func prepareCamera() throws {
    videoSession = AVCaptureSession()
    videoSession.sessionPreset = AVCaptureSession.Preset.photo
    previewLayer = AVCaptureVideoPreviewLayer(session: videoSession)
    previewLayer.videoGravity = .resizeAspectFill
    
    // let devices = AVCaptureDevice.devices()
    
    // cameraDevice = devices.filter { $0.hasMediaType(.video) }.compactMap { $0 }.first
    // 2022-08-03 YY Grab a camera device by device name
    let deviceDiscoverySession = AVCaptureDevice.DiscoverySession.init(deviceTypes: [AVCaptureDevice.DeviceType.builtInWideAngleCamera, AVCaptureDevice.DeviceType.externalUnknown], mediaType: .video, position: AVCaptureDevice.Position.unspecified)
      
    // Set "eGlass" device
    for device in deviceDiscoverySession.devices{

        if device.localizedName.lowercased().contains("eglass"){
            cameraDevice = device
            break
        }
    }
    // Set the first device
    if cameraDevice == nil{
        cameraDevice = deviceDiscoverySession.devices.first
    }
    
    if cameraDevice != nil  {
      do {
        let input = try AVCaptureDeviceInput(device: cameraDevice)
        if videoSession.canAddInput(input) {
          videoSession.addInput(input)
        } else {
          throw CameraError.cannotAddInput
        }
        
        if let connection = previewLayer.connection, connection.isVideoMirroringSupported {
          connection.automaticallyAdjustsVideoMirroring = false
          // 2022-07-22 YY turn off mirrored
          connection.isVideoMirrored = false
        } else {
          throw CameraError.previewLayerConnectionError
        }
        
        previewLayer.frame = containerView.bounds
        containerView.layer = previewLayer
        containerView.wantsLayer = true
        
      } catch {
        throw CameraError.cannotDetectCameraDevice
      }
    }
    
    let videoOutput = AVCaptureVideoDataOutput()
    videoOutput.setSampleBufferDelegate(self, queue: cameraQueue)
    if videoSession.canAddOutput(videoOutput) {
      videoSession.addOutput(videoOutput)
    } else {
      throw CameraError.cannotAddOutput
    }
  }
  
    public func startSession() throws {
    if let videoSession = videoSession {
      if !videoSession.isRunning {
        cameraQueue.async {
          videoSession.startRunning()
        }
      }
    } else {
      throw CameraError.videoSessionNil
    }
  }
  
    public func stopSession() throws {
    if let videoSession = videoSession {
      if videoSession.isRunning {
        cameraQueue.async {
          videoSession.stopRunning()
        }
      }
    } else {
      throw CameraError.videoSessionNil
    }
  }
}




// MARK: - AVCaptureVideoDataOutputSampleBufferDelegate

extension CameraManager: AVCaptureVideoDataOutputSampleBufferDelegate {
    public func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
      
    delegate?.cameraManager(output, didOutput: sampleBuffer, from: connection)
            
  }
}



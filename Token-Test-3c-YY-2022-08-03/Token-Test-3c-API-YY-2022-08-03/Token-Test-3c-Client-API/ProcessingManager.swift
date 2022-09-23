/* ------------------------------------------------------------------------------------------------------*
* Company Name : CTI One Corporation                                                                     *
* Program name : ProcessingManager.swift (Testing)                                                       *
* Coded By     : ZW                                                                                      *
* Date         : 2022-07-22                                                                              *
* Updated By   : YY                                                                                      *
* Date         : 2022-08-02                                                                              *
* Version      : v1.1.1                                                                                  *
* Copyright    : Copyright (c) 2022 CTI One Corporation                                                  *
* Purpose      : CV100_Token_Testing_3c                                                                  *
*              : Integrate TT2a. Shows a original video and processed video side by side                 *
*              : v1.0.0 2022-07-22 ZW Create                                                             *
*              : v1.1.0 2022-07-25 YY Modify sending and receiving part                                  *
*              : v1.1.1 2022-08-02 YY Add autoreleasepool[] to release NSImage, PNG objects              *
*---------------------------------------------------------------------------------------------------------*/


import Foundation
import AppKit

public class ProcessingManager {

    // var recvFlag = 1
    var originalNSImage : NSImage!
    // var resultNSImage : NSImage!
    
    public var processingClient : Client! // Do NOT use "localhost". It causes the connection error once
    public init(){
        
    }

    public func start(server: String, port: UInt16) {
        Thread.detachNewThread{
            self.startThread(server: server, port: port)
        }
    }
    
    public func startThread(server: String, port: UInt16) {
        
        processingClient = Client(host: server, port: port)
        processingClient.start()
        //Thread.sleep(forTimeInterval: 3)
                
        while (true){
            //receive flag turn on
            // 2022-07-26 YY Remove recvFlag
            // if recvFlag == 1 && originalNSImage != nil {
            autoreleasepool{
                if originalNSImage != nil {
                    // Convert a original image from NSImage to PNG Data
                    guard let unwrappedNSImage = originalNSImage else {
                        //continue
                        return
                        
                    }
                    
                    unwrappedNSImage.cgImage(forProposedRect: nil, context: nil, hints: nil)
                    
                    guard let originalCGImage = unwrappedNSImage.cgImage(forProposedRect: nil, context: nil, hints: nil) else{
                        //print("originalCGImage is nil")
                        //originalNSImage = nil
                        //continue
                        return
                    }
                
                    let bitmapImgRep = NSBitmapImageRep(cgImage: originalCGImage)
                    
                    guard let pngData = bitmapImgRep.representation(using: .png, properties: [:]) else { return }
                    
                    processingClient.connection.send(data: (pngData) as Data)
                    //print("Send data ProcessingManager.startThread:", Date(), " size: ", pngData.count)
                    
                    //processingClient.connection.send(data: imageData)
                    //originalNSImage = nil
                }
            }
        }
        
        // 2022-06-07 YY Send a image once
        /* while(true) {
            var command = readLine(strippingNewline: true)
            switch (command){
         case "CRLF":
                    command = "\r\n"
                case "RETURN":
                    command = "\n"
                case "exit":
                    client.stop()
                default:
                    break
            }
            client.connection.send(data: (command?.data(using: .utf8))!)
        } */
        
    }

    public func getResultImage() -> NSImage{
        return processingClient.getImageData()
    }
    public func setImage(image: NSImage){
        originalNSImage = image
        
    }
}








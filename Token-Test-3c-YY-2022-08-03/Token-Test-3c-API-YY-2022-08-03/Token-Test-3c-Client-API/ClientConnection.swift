/* ------------------------------------------------------------------------------------------------------*
* Company Name : CTI One Corporation                                                                     *
* Program name : ClientConnection.swift (Testing)                                                        *
* Coded By     : ZW                                                                                      *
* Date         : 2022-06-07                                                                              *
* Updated By   :                                                                                         *
* Date         :                                                                                         *
* Version      : v1.0.0                                                                                  *
* Copyright    : Copyright (c) 2022 CTI One Corporation                                                  *
* Purpose      : Send/Receive an image via TCP/IP                                                        *
*              : v1.0.0 2022-06-07 ZW Create                                                             *
---------------------------------------------------------------------------------------------------------*/


import Foundation
import Network
import AppKit

@available(macOS 10.14, *)
@available(iOS 12.0, *)
public class ClientConnection {

    let nwConnection: NWConnection
    let queue = DispatchQueue(label: "Client connection Q")
    var imageData = Data()
    var resultNSImage : NSImage!
    // public var checkNum = 0
    
    
    //init(nwConnection: NWConnection) {
     //   self.nwConnection = nwConnection
        
    //}
    
    init(nwConnection: NWConnection){
        self.nwConnection = nwConnection
    }

    var didStopCallback: ((Error?) -> Void)? = nil

    func start() {
        //print("connection will start")
        nwConnection.stateUpdateHandler = stateDidChange(to:)
        setupReceive()
        nwConnection.start(queue: queue)
    }

    private func stateDidChange(to state: NWConnection.State) {
        switch state {
        case .waiting(let error):
            connectionDidFail(error: error)
        case .ready:
            var param = 1
            //print("Client connection ready")
        case .failed(let error):
            connectionDidFail(error: error)
        default:
            break
        }
    }

    public func setupReceive() {
        // print("setupReceive")
        nwConnection.receive(minimumIncompleteLength: 1, maximumLength: 6553600) { (data, _, isComplete, error) in
            
            
            if let data = data, !data.isEmpty {
                /*
                let message = String(data: data, encoding: .utf8)
                print("connection did receive, data: \(data as NSData) string: \(message ?? "-" )")
                 */
                // print("data.count: \(data.count)")
                self.imageData.append(data)
                
            }
            let str = String(decoding: self.imageData, as: UTF8.self)
            if str.contains("IEND"){
           
                //self.getProcessedIamge()
                let resultDataNSImage = NSImage(data: self.imageData)
                if(resultDataNSImage?.size == nil){
                    //print("Received Data is nil")
                }else{
                    self.resultNSImage = resultDataNSImage
                }
                
                // self.checkNum = 1
                self.imageData.removeAll()
                
            }
            if isComplete {
                print("Connection END")
                self.connectionDidEnd()
            } else if let error = error {
                self.connectionDidFail(error: error)
            } else {
                self.setupReceive()
            }
        }
    }

    func send(data: Data) {
        nwConnection.send(content: data, completion: .contentProcessed( { error in
            if let error = error {
                self.connectionDidFail(error: error)
                return
            }
            //print("connection did send, data: \(data as NSData)")
        }))
    }

    func stop() {
        print("connection will stop")
        stop(error: nil)
    }

    private func connectionDidFail(error: Error) {
        print("connection did fail, error: \(error)")
        self.stop(error: error)
    }
    
    /*
    func getCheckNum() ->Int{
        return checkNum
    }
    
    func setCheckNum(_ newNum: Int){
        checkNum = newNum
        
    }
    */
    /*
    public func getProcessedIamge(){
        //"/Users/chriswang/Desktop/ImageSendReceive/testimage.png"
        let addressStr = "/Users/chriswang/Desktop/CTIOneAppDevelopment-ZW-2021-07-01/OpenCVCannyEdge/testimage.png"
        
        let fileUrl = URL(fileURLWithPath: addressStr)
        print(addressStr)
        let dest = CGImageDestinationCreateWithURL(fileUrl as CFURL, kUTTypePNG, 1, nil)
        let nsImage = NSImage(data: self.imageData)
        guard let cgiImage = nsImage?.cgImage(forProposedRect: nil, context: nil, hints: nil) else{return}
        CGImageDestinationAddImage(dest!, cgiImage, nil)
        CGImageDestinationFinalize(dest!)
        //self.stop(error: nil)
        
    }
    */
    
    public func getImageData() -> NSImage{
        while(true)
        {
            // if checkNum == 1 {
            if resultNSImage != nil{
                break
            }
        }
        // self.checkNum = 0
        return resultNSImage
    }
    
    private func connectionDidEnd() {
        print("connection did end")
    }

    private func stop(error: Error?) {
        self.nwConnection.stateUpdateHandler = nil
        self.nwConnection.cancel()
        if let didStopCallback = self.didStopCallback {
            self.didStopCallback = nil
            didStopCallback(error)
        }
    }
}









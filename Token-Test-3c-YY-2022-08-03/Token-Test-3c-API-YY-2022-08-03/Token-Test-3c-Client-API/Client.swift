/* ------------------------------------------------------------------------------------------------------*
* Company Name : CTI One Corporation                                                                     *
* Program name : Client.swift (Testing)                                                                  *
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
public class Client {
    let connection: ClientConnection
    let host: NWEndpoint.Host
    let port: NWEndpoint.Port
    
    //public init(host: String, port: UInt16) {
     //   self.host = NWEndpoint.Host(host)
    //    self.port = NWEndpoint.Port(rawValue: port)!
    //    let nwConnection = NWConnection(host: self.host, port: self.port, using: .tcp)
    //    connection = ClientConnection(nwConnection: nwConnection)
   // }
    
    public init(host: String, port: UInt16) {
        self.host = NWEndpoint.Host(host)
        self.port = NWEndpoint.Port(rawValue: port)!
        let nwConnection = NWConnection(host: self.host, port: self.port, using: .tcp)
        connection = ClientConnection(nwConnection: nwConnection)
    }
    

    public func start() {
        //print("Client started \(host) \(port)")
        print("Client started")
        connection.didStopCallback = didStopCallback(error:)
        connection.start()
    }

    public func stop() {
        connection.stop()
    }

    public func send(data: Data) {
        connection.send(data: data)
    }

    public func didStopCallback(error: Error?) {
        if error == nil {
            exit(EXIT_SUCCESS)
        } else {
            exit(EXIT_FAILURE)
        }
    }
    
    public func getImageData() -> NSImage{
        connection.getImageData()
    }
    
    /*
    public func getCheckNum() -> Int{
        connection.getCheckNum()
    }
    
    public func setCheckNum(_ newNum: Int){
        connection.setCheckNum(newNum)
    }
     */
}









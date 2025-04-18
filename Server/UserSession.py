from UserInterFace import LoginUsers
from Message import decodeMessage, createMessage
from MergeRequest import MergeRequest
import sqlite3
import hashlib
import subprocess
import os
import json
import sys
import importlib.util
import random
class UserSession:
    def __init__(self, client, username):
        self.client = client
        self.username = username
        self.mergeDB = MergeRequest()

    def run(self):
        while True:
            self.client.sendall(createMessage("info", LoginUsers.getInitUI(), True))
            msg = decodeMessage(self.client.recv(1024))
            option = msg["data"]

            if option == '1': #Check Online User
                online = LoginUsers._OnlineLoginUsers
                userList = "\n".join(online.keys())
                self.client.sendall(createMessage("info", userList, False))
            elif option == '2': #send Merge Request
                self.option2()
                pass
            elif option == '3':#check merge Request
                self.option3()
                pass
            elif option == '4':#confirm merge request
                self.option4()
                pass
            elif option == '5':#start merge request
                self.option5()
                pass
            elif option == '6':
                self.option6()
                pass
            elif option == '7':#upload to IPFS
                self.option7()
                pass
            elif option == '8':#get partner CID
                self.option8()
                pass
            elif option == '9':#download from IPFS
                self.option9()
                pass
            elif option == '10':#start PSI protocol
                self.option10()
                pass
            elif option == '11':#PSI exchange CID step
                self.option11()
                pass
            elif option == 'Q':
                LoginUsers.update_Online_LoginUsers(self.username,self.client ,False)
                self.client.sendall(createMessage("info", "Logging out...", False))
                break
            else:
                self.client.sendall(createMessage("info", "Invalid option", False))
    def option2(self):
        self.client.sendall(createMessage("info","Merge Partner:",True))
        username2 = decodeMessage(self.client.recv(1024))["data"]
        usernames = sorted([self.username, username2])
        combined = f"{usernames[0]}_{usernames[1]}".encode()
        requestID = hashlib.sha256()
        requestID.update(combined)

        try:
            self.mergeDB.createMergeRequest(RequestID=requestID.hexdigest(),username1=usernames[0], username2 =usernames[1])
        except ValueError as e:
            self.client.sendall(createMessage("info", f"{e}",False))
        except sqlite3.IntegrityError as ie:
            self.client.sendall(createMessage("info", f"{ie}",False))
    def option3(self):
        try:
            result = "\n".join(self.mergeDB.checkAllMergeRequest(self.username))
            self.client.sendall(createMessage("info", result, False))
        except Exception as e:
            print(f"{e}")
        
        ...
    def option4(self):
        self.client.sendall(createMessage("info", "RequestsID:",True))
        requestID = decodeMessage(self.client.recv(1024))["data"]
        try:
            self.mergeDB.confirmMergeRequest(requestID,self.username)
            self.client.sendall(createMessage("info", "Confirm success", False))
        except Exception as e:
            print(f"{e}")
        ...
    def option5(self):
        """
            if requestID Exists
            if both users confirmed the request
            if both users are online
            send signal 
            both users start encrypt threading process
        """
        self.client.sendall(createMessage("info","RequestsID",True))

        
        requestID = decodeMessage(self.client.recv(1024))["data"]
        try:
            data = self.mergeDB.getRequest(requestID)
            username1, username2 ,user1_confirm, user2_confirm = data[1:5]
        except ValueError as e:
            self.client.sendall(createMessage("info", f"{e}",False))
            ...
        if not (user1_confirm and user2_confirm):
            self.client.sendall(createMessage("info","request hasn't been confirmed by both parties", False))
            return
        bothUserOnline = (username1 in LoginUsers._OnlineLoginUsers) and (username2 in LoginUsers._OnlineLoginUsers)
        if not bothUserOnline:
            self.client.sendall(createMessage("info","Both user must be online", False))
            return
        client1 = LoginUsers._OnlineLoginUsers[username1]
        client2 = LoginUsers._OnlineLoginUsers[username2]
        client1.sendall(createMessage("signal",f"{requestID}", False))
        client2.sendall(createMessage("signal",f"{requestID}", False))
    def option6(self):
        """
        Send a signal to the client to record CID in local database
        """
        self.client.sendall(createMessage("info","RequestsID",True))
        requestID = decodeMessage(self.client.recv(1024))["data"]
        self.client.sendall(createMessage("info" , "CID" , True))
        CID = decodeMessage(self.client.recv(1024))["data"]
        
        try:
            # Send CID to server database
            self.mergeDB.insertCID(self.username, requestID, CID)
            
            # Send signal to client to record in local database
            record_info = {
                "request_id": requestID,
                "cid": CID
            }
            self.client.sendall(createMessage("signal", f"record_my_cid:{json.dumps(record_info)}", False))
            
            # Wait for client's response
            response = decodeMessage(self.client.recv(1024))
            
            if response["type"] == "info" and "success" in response["data"].lower():
                self.client.sendall(createMessage("info", "CID recorded successfully on server and local database", False))
            else:
                self.client.sendall(createMessage("info", f"CID recorded on server, but client reported: {response['data']}", False))
                
        except ValueError as E:
            self.client.sendall(createMessage("info", f"{E}", False))
        
    def option7(self):
        """
        Send a signal to the client to upload files to IPFS
        """
        self.client.sendall(createMessage("signal", "upload_to_ipfs", False))
        # Wait for the client to respond with the CID
        response = decodeMessage(self.client.recv(1024))
        if response["type"] == "info":
            self.client.sendall(createMessage("info", response["data"], False))
        else:
            self.client.sendall(createMessage("info", "Failed to get CID from client", False))
    
    def option8(self):
        """
        Get the partner's CID from the server and signal client to store it
        """
        self.client.sendall(createMessage("info", "Enter RequestID to get partner's CID:", True))
        requestID = decodeMessage(self.client.recv(1024))["data"]
        
        try:
            # Get the merge request data from the server
            data = self.mergeDB.getRequest(requestID)
            
            # Extract user IDs and CIDs
            request_id, user1_id, user2_id, _, _, user1_cid, user2_cid = data
            
            # Determine which user is the partner and get their CID
            if self.username == user1_id:
                partner_username = user2_id
                partner_cid = user2_cid
            elif self.username == user2_id:
                partner_username = user1_id
                partner_cid = user1_cid
            else:
                self.client.sendall(createMessage("info", "You are not part of this merge request", False))
                return
            
            if not partner_cid:
                self.client.sendall(createMessage("info", f"Partner {partner_username} has not uploaded a CID yet", False))
                return
            
            # Send signal to client to record partner CID
            partner_info = {
                "request_id": requestID,
                "partner_cid": partner_cid
            }
            self.client.sendall(createMessage("signal", f"record_partner_cid:{json.dumps(partner_info)}", False))
            
            # Wait for client's response
            response = decodeMessage(self.client.recv(1024))
            
            # Display CID info to the user
            result_info = f"Partner {partner_username}'s CID: {partner_cid}\n"
            
            if response["type"] == "info" and "success" in response["data"].lower():
                result_info += "This CID has been saved to your local database.\n"
            else:
                result_info += f"Warning: {response['data']}\n"
                
            result_info += "To retrieve their files: ipfs get " + partner_cid
            
            self.client.sendall(createMessage("info", result_info, False))
            
        except ValueError as e:
            self.client.sendall(createMessage("info", f"Error: {e}", False))
        except Exception as e:
            self.client.sendall(createMessage("info", f"Unexpected error: {e}", False))
    
    def option9(self):
        """
        Send CID and download path to client for IPFS download
        """
        self.client.sendall(createMessage("info", "Enter the CID to download from IPFS:", True))
        cid = decodeMessage(self.client.recv(1024))["data"]
        
        if not cid:
            self.client.sendall(createMessage("info", "Error: No CID provided", False))
            return
        
        # Ask for download location
        self.client.sendall(createMessage("info", "Enter download location (leave blank for default 'Downloaded_Data'):", True))
        download_path = decodeMessage(self.client.recv(1024))["data"]
        
        if not download_path:
            download_path = "Downloaded_Data"
        
        # Send signal to client with CID and download path
        download_info = {
            "cid": cid,
            "download_path": download_path
        }
        self.client.sendall(createMessage("signal", f"download_from_ipfs:{json.dumps(download_info)}", False))
        
        # Wait for client's response
        response = decodeMessage(self.client.recv(1024))
        self.client.sendall(createMessage("info", response["data"], False))
    
    def option10(self):
        """
        Start PSI protocol - Step 1: Initialize and compute first blinded values
        """
        # Ask for Excel file path
        self.client.sendall(createMessage("info", "Enter Excel file path:", True))
        excel_path = decodeMessage(self.client.recv(1024))["data"]
        
        # Ask for identifier columns
        self.client.sendall(createMessage("info", "Enter identifier columns (comma-separated, e.g. 's_id,p_id,s_sex'):", True))
        id_columns_str = decodeMessage(self.client.recv(1024))["data"]
        id_columns = [col.strip() for col in id_columns_str.split(',')]
        
        # Ask for data columns
        self.client.sendall(createMessage("info", "Enter data columns to share (comma-separated, e.g. 'county,region'):", True))
        data_columns_str = decodeMessage(self.client.recv(1024))["data"]
        data_columns = [col.strip() for col in data_columns_str.split(',')]
        
        # Ask for private key
        self.client.sendall(createMessage("info", "Enter your private key (integer):", True))
        private_key_str = decodeMessage(self.client.recv(1024))["data"]
        try:
            private_key = int(private_key_str)
        except ValueError:
            self.client.sendall(createMessage("info", "Invalid private key. Please enter an integer.", False))
            return
        
        # Ask for shared prime
        self.client.sendall(createMessage("info", "Enter the shared prime number:", True))
        prime_str = decodeMessage(self.client.recv(1024))["data"]
        try:
            prime = int(prime_str)
        except ValueError:
            self.client.sendall(createMessage("info", "Invalid prime number. Please enter an integer.", False))
            return
        
        # Generate private key (待修改)
        private_key = random.randint(2, prime-2)
        
        # Create PSI parameters
        psi_params = {
            "excel_path": excel_path,
            "id_columns": id_columns,
            "data_columns": data_columns,
            "private_key": private_key,
            "prime": prime
        }
        
        # Send signal to client to start PSI protocol
        self.client.sendall(createMessage("signal", f"psi_start:{json.dumps(psi_params)}", False))
        
        # Wait for client's response with CID
        response = decodeMessage(self.client.recv(1024))
        
        if response["type"] == "info":
            self.client.sendall(createMessage("info", response["data"] + "\n\nShare this CID with your PSI partner and continue with Option 11.", False))
        else:
            self.client.sendall(createMessage("info", "Failed to start PSI protocol", False))
    
    def option11(self):
        """
        Continue PSI protocol by exchanging CIDs
        """
        # Ask which step to continue
        self.client.sendall(createMessage("info", "Enter PSI step number (2, 3, or 4):", True))
        step_str = decodeMessage(self.client.recv(1024))["data"]
        
        try:
            step = int(step_str)
            if step not in [2, 3, 4]:
                raise ValueError("Step must be 2, 3, or 4")
        except ValueError:
            self.client.sendall(createMessage("info", "Invalid step number. Please enter 2, 3, or 4.", False))
            return
        
        # Ask for partner's CID
        self.client.sendall(createMessage("info", f"Enter your partner's CID for step {step-1}:", True))
        partner_cid = decodeMessage(self.client.recv(1024))["data"]
        
        # Send signal to client to continue PSI protocol
        signal_type = f"psi_step{step}:{partner_cid}"
        self.client.sendall(createMessage("signal", signal_type, False))
        
        # Wait for client's response
        response = decodeMessage(self.client.recv(1024))
        
        if response["type"] == "info":
            if step < 4:
                self.client.sendall(createMessage("info", response["data"] + "\n\nShare this CID with your PSI partner and continue with Option 11 for the next step.", False))
            else:
                self.client.sendall(createMessage("info", response["data"] + "\n\nPSI protocol completed successfully!", False))
        else:
            self.client.sendall(createMessage("info", f"Failed to execute PSI step {step}", False))

    def __del__(self):
        # No need to close the database connection anymore
        pass
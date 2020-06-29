#!/usr/bin/python3
import sys
import os
import os.path
import subprocess
from os import path
#JUST TO KNOW THE TERMINAL WIDTH
tput_out = subprocess.run(['tput','cols'],stdout=subprocess.PIPE)
shell_width = int(tput_out.stdout.decode('utf-8'))
#GET USER ENV AND CHECK PWD MAYBE LATER
#Ask for definitive path or !(relative path) to apk
if len(sys.argv) != 2:
        print("Usage: python autandro.py <apk_file_path>")
        exit()
apkpath = sys.argv[1]
#print("$"*shell_width)
#print("DEBUG: File extension Check value: " + apkpath[-4:])
#print("DEBUG: Supplied apkpath:" + apkpath)
#print("$"*shell_width)
#Ask for output folder name (combined for jadx-gui and apktool)
tool_folder_name = ''
rest_char = ['#','%','&','{','}','\\','<','>','\*','\?','/',' ','\$','\!','\'','\"','\:','\@','\+','\`','\|',"\="]

if ((path.exists(apkpath) == 'False') or (apkpath[-4:] != '.apk') ):
        print("Specified file: " + apkpath + " Is not Valid.\nPlease Use a valid file!")
        exit()
else:
        tool_folder_name = (apkpath.split('/')[-1]).split('.apk')[0]
#        print("$"*shell_width)
#        print("DEBUG: tool_folder_name value before operation: " + tool_folder_name)
#        print("$"*shell_width)
        for i in tool_folder_name:
                if (i in rest_char):
                        tool_folder_name = tool_folder_name.replace(i,'a')
                else:
                        continue
base_path = (((apkpath[::-1]).split('kpa.')[1])[((apkpath[::-1]).split('kpa.')[1]).index('/'):])[::-1]
#print("DEBUG: base_path value: " + base_path)
#print("DEGUB: tool_folder_name value after operation: " + tool_folder_name)
apktool_folder_name = "apktool_" + tool_folder_name
#print("DEBUG: apktool_folder_name value: " + apktool_folder_name)
jadx_folder_name = "jadx_" + tool_folder_name
#print("DEBUG: jadx_folder_name value: " + jadx_folder_name)
#Running apktool d apkpath -o apktool_folder_name
if path.exists(base_path+apktool_folder_name):
        print("Apktool output folder already present, Using it!")
else:
        apktool_exec = 'apktool d ' + apkpath + ' -o ' + base_path + apktool_folder_name
        os.system(apktool_exec)

#Running mkdir
jadx_dir = "mkdir " + base_path + jadx_folder_name
if path.exists(base_path+jadx_folder_name):
        print("jadx folder already exists!")
else:
        os.system(jadx_dir)

#Function for returning exported components from AndroidManifest.xml
def manifest_export_parser(apktool_output_path):
        print("\n\n")
        print("$"*shell_width)
        print("Parsing AndroidManifest.xml for Exported components in: "+ apktool_output_path)
        print("$"*shell_width)
        print("\n\n")
#PLAN: read manifest line by line performing ops only on lines that are within <application></application>
#tag, even in them activity, service and provider are checked for export
#in android < 4.2 everything not explicitly exported=false is exported. On match print full line for better context as it maybe permission protected
        manifest_file_path = apktool_output_path + "/AndroidManifest.xml"
        match_string = " android:exported=\"true\" "
        with open(manifest_file_path) as mfile:
                line_num = 1
                for line in mfile:
                        if match_string in line:
                                print("="*shell_width)
                                print("EXPORTED COMPONENT AT LINE NUMBER: " + str(line_num))
                                print("="*shell_width)
                                print(line)
                                #uselss part below
                                #component_type = ((line.split(' ')[0]).split('<')[1])
                                #component_name = line.split(' ')
                                line_num = line_num + 1
                        else:
                                line_num = line_num + 1
        return;

def manifest_main_launcher_parser(apktool_out_path):
        print('\n\n')
        print("$"*shell_width)
        print('Initialising MAIN intent & LAUNCHER category Search in:' + apktool_out_path)
        print("$"*shell_width)
        print("\n\n")
        manifest_file_path = apktool_out_path + "/AndroidManifest.xml"
        with open(manifest_file_path) as mfile:
                line_num = 1
                useful_block_flag = 0
                main_found_flag = 0
                launcher_found_flag = 0
                final_output_list = []
                useful_line_list = []
                for line in mfile:
                        if (useful_block_flag == 1) and (main_found_flag == 0) and (launcher_found_flag == 0):
                                useful_line_list.append(line)
                                if ("android.intent.action.MAIN" in line):
                                        main_found_flag = 1
                                elif (("</activity>" in line) or ("</receiver>" in line) or ("</service>" in line) or ("</provider>" in line)):
                                        useful_line_list = []
                                        useful_block_flag = 0
                                else:
                                        useful_line_list.append(line)
                        elif ((useful_block_flag == 1) and (main_found_flag == 1) and (launcher_found_flag == 0)):
                                if ("android.intent.category.LAUNCHER" in line):
                                        launcher_found_flag = 1
                                        useful_line_list.append(line)
                                elif (("</activity>" in line) or ("</receiver>" in line) or ("</service>" in line) or ("</provider>" in line)):
                                        useful_line_list = []
                                        useful_block_flag = 0
                                        main_found_flag = 0
                                else:
                                        useful_line_list.append(line)
                        elif ((useful_block_flag == 1) and (main_found_flag == 1) and (launcher_found_flag == 1)):
                                if (("</activity>" in line) or ("</receiver>" in line) or ("</service>" in line) or ("</provider>" in line)):
                                        useful_line_list.append(line)
                                        final_output_list.append(useful_line_list)
                                        useful_line_list = []
                                        useful_block_flag = 0
                                        main_found_flag = 0
                                        launcher_found_flag = 0
                                else:
                                        useful_line_list.append(line)
                        else:
                                if ((("<activity" in line) or ("<provider" in line) or ("<service" in line) or ("<receiver" in line)) and ("/>" not in line)):
                                        useful_block_flag = 1
                                        useful_line_list.append(line)
                                else:
                                        continue
                for i in final_output_list:
                        print("="*shell_width)
                        print("Code Block Containing Main intent and Launcher category:")
                        print("="*shell_width)
                        for j in i:
                                print(j) 
manifest_export_parser(base_path + apktool_folder_name)
manifest_main_launcher_parser(base_path + apktool_folder_name)

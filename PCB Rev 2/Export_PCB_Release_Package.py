import subprocess
import os
from enum import Enum
import shutil

class ERROR_CODES(Enum):
    ALL_OK = 0
    PATHS_DO_NOT_EXIST = 1
    REVISION_INFO_INVALID = 2
    COULD_NOT_CREATE_FOLDER = 3
    REVISION_ALREADY_EXISTS = 4

# Export Parameters
ProjectName = "VolDisp"

MainSchematicFile = "VolumetricDisplay.kicad_sch"
MainPCBFile = "VolumetricDisplay.kicad_pcb"
GerberLayers = "F.Cu,B.Cu,In1.Cu,In2.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts,User.1"


ReleasesFolder = ".\\Releases"
SchematicPrefix = "SCH_"
GerbersPrefix = "CAM_"
FabPrefix = "FAB_"
StepPrefix = "STEP_"
PositionPrefix = "PNP_"
BillOfMaterialsPrefix = "BOM_"

# System Parameters
KICAD_CLI_PATH = "C:\\Program Files\\KiCad\\10.0\\bin\\"

# Constants
KICAD_CLI_EXE = KICAD_CLI_PATH + "kicad-cli.exe"

# Helper Functions:

def deleteDir(pathToDel):
    for root, dirs, files in os.walk(pathToDel, topdown=False):
        # Delete all files in the current directory
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
                    
        # Delete all empty subdirectories (now empty after deleting files)
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            os.rmdir(dir_path)
    os.rmdir(pathToDel)

# Export steps:

def arePathsValid():
    pathsAreValid = True
    pathsAreValid &= os.path.exists(KICAD_CLI_EXE)
    if(not pathsAreValid):
        print("\x1B[31mCannot run without kicad cli\x1B[39m")
        return
    pathsAreValid &= os.path.exists(MainSchematicFile)
    if(not pathsAreValid):
        print("\x1B[31mCannot find schematic file \"{}\" x1B[39m".format(MainSchematicFile))
        return
    return pathsAreValid

def collectRevisionInfo():
    nameIsvalid = False
    revisionName = ""
    folders = [d for d in os.listdir(ReleasesFolder) if os.path.isdir(os.path.join(ReleasesFolder, d))]
    print("\x1B[33mPrevious Revisions:\x1B[39m")
    print(folders)
    while not nameIsvalid:
        revisionName = input("\x1B[33mNew Release Name:\x1B[39m")
        if(revisionName != ""):
            nameIsvalid = True
    return revisionName

def createRevisionFolder(currReleaseName):
    currExportFolder = ReleasesFolder + "\\" + currReleaseName
    if(os.path.exists(currExportFolder)):
        print("\x1B[33mRelease Folder Already Exists!\x1B[39m")
        shouldContinue = ""
        while(shouldContinue != "Y" and shouldContinue != "N" and shouldContinue != "YES" and shouldContinue != "NO"):
            shouldContinue = input("\x1B[32mContinue? \x1B[33mAll files in release package will be deleted! \x1B[32m(Y/N): \x1B[39m")
            shouldContinue = shouldContinue.upper().replace("\r", "").replace("\n", "")
        if(shouldContinue == "N" or shouldContinue == "NO"):
            return ""
        deleteDir(currExportFolder)
    os.mkdir(currExportFolder)
    return currExportFolder

def createDirectory():
    if(not(os.path.exists(ReleasesFolder))):
        os.mkdir(ReleasesFolder)

# # kicad-cli sch export pdf -o [file] [*.kicad_sch]
def exportSchematic(currExportFolder, currReleaseName):
    schFileName = currExportFolder + "\\" + SchematicPrefix + ProjectName + "_" + currReleaseName + ".pdf"
    print("\x1B[32mExporting Schematics into file [{}]\x1B[39m".format(schFileName))
    result = subprocess.run([KICAD_CLI_EXE, "sch", "export", "pdf", "-o", schFileName, 
                             MainSchematicFile], capture_output=True, text=True)
    print(result.stdout)

# kicad-cli pcb export gerbers [--output OUTPUT_DIR] INPUT_FILE.kicad_pcb   
# kicad-cli pcb export drill [--output OUTPUT_DIR] INPUT_FILE.kicad_pcb   

def exportGerbers(currExportFolder, currReleaseName):
    camFileDir = currExportFolder + "\\" + GerbersPrefix + ProjectName + "_" + currReleaseName
    print("\x1B[32mExporting Gerbers into folder [{}]\x1B[39m".format(camFileDir))
    os.mkdir(camFileDir)
    result = subprocess.run([KICAD_CLI_EXE, "pcb", "export", "gerbers", "-o", camFileDir, 
                                "-l", GerberLayers, MainPCBFile], capture_output=True, text=True)
    print(result.stdout)
    print("\x1B[32mExporting Drill Files into folder [{}]\x1B[39m".format(camFileDir))
    result = subprocess.run([KICAD_CLI_EXE, "pcb", "export", "drill", "-o", camFileDir, 
                                MainPCBFile], capture_output=True, text=True)
    print(result.stdout)
    print("\x1B[32mZipping folder [{}] into file {}.zip\x1B[39m".format(camFileDir, camFileDir))
    shutil.make_archive(camFileDir, 'zip', camFileDir)
    print("\x1B[32mCleaning up Folder [{}]\x1B[39m".format(camFileDir))
    deleteDir(camFileDir)

def exportFabDocument(currExportFolder, currReleaseName):
    fabFilePath = currExportFolder + "\\" + FabPrefix + ProjectName + "_" + currReleaseName + ".pdf"
    print("\x1B[32mExporting Fabrication Document [{}]\x1B[39m".format(fabFilePath))
    result = subprocess.run([KICAD_CLI_EXE, "pcb", "export", "pdf", "-o", fabFilePath, "--include-border-title",  
                                    "-l", GerberLayers, "--mode-multipage", MainPCBFile], capture_output=True, text=True)
    print(result.stdout)

def exportStepRenders(currExportFolder, currReleaseName):
    stepFilePath = currExportFolder + "\\" + StepPrefix + ProjectName + "_" + currReleaseName + ".step"
    print("\x1B[32mExporting 3D model [{}]\x1B[39m".format(stepFilePath))
    result = subprocess.run([KICAD_CLI_EXE, "pcb", "export", "step", "-o", stepFilePath,  
                                    MainPCBFile], capture_output=True, text=True)
    print(result.stdout)

# kicad-cli pcb export pos MyPCB.kicad_pcb --format csv --units mm -o MyPCB.positions.csv   

def generatePositionFiles(currExportFolder, currReleaseName):
    stepFilePath = currExportFolder + "\\" + PositionPrefix + ProjectName + "_" + currReleaseName + ".csv"
    print("\x1B[32mExporting Position File [{}]\x1B[39m".format(stepFilePath))
    result = subprocess.run([KICAD_CLI_EXE, "pcb", "export", "pos", MainPCBFile, "-o", stepFilePath, "--format", "csv",
                                    "--units", "mm"], capture_output=True, text=True)
    print(result.stdout)

def generateBillOfMaterials(currExportFolder, currReleaseName):
    bomFilePath = currExportFolder + "\\" + BillOfMaterialsPrefix + ProjectName + "_" + currReleaseName + ".csv"
    print("\x1B[32mExporting Bill Of Materials [{}]\x1B[39m".format(bomFilePath))
    result = subprocess.run([KICAD_CLI_EXE, "sch", "export", "bom", MainSchematicFile, "-o", bomFilePath
                                ], capture_output=True, text=True)
    print(result.stdout)

# MainProgram:

def main():
    print("\x1B[32mKiCad Export Script\x1B[39m")
    if(not(arePathsValid())):
        print("\x1B[32mclosing\x1B[39m")
        return ERROR_CODES.PATHS_DO_NOT_EXIST
    print("\x1B[32mPaths are valid\x1B[39m")
    createDirectory()
    
    currReleaseName = collectRevisionInfo()
    currExportFolder = createRevisionFolder(currReleaseName)
    if (currExportFolder == ""):
        return ERROR_CODES.REVISION_ALREADY_EXISTS
    
    exportSchematic(currExportFolder, currReleaseName)
    exportGerbers(currExportFolder, currReleaseName)
    exportFabDocument(currExportFolder, currReleaseName)
    exportStepRenders(currExportFolder, currReleaseName)
    generatePositionFiles(currExportFolder, currReleaseName)
    generateBillOfMaterials(currExportFolder, currReleaseName)
    

    print("\x1B[32mExport Finished\x1B[39m")
    return ERROR_CODES.ALL_OK

if __name__ == "__main__":
    main()
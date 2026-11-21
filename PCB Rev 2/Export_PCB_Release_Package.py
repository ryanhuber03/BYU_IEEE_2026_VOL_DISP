import subprocess
import os
from enum import Enum
import shutil
from dataclasses import dataclass, field
from datetime import date

class ERROR_CODES(Enum):
    ALL_OK = 0
    PATHS_DO_NOT_EXIST = 1
    REVISION_INFO_INVALID = 2
    COULD_NOT_CREATE_FOLDER = 3
    REVISION_ALREADY_EXISTS = 4

@dataclass(repr=False)
class ManifestItem:
    filename: str = ""
    description: str = ""
    def __str__(self):
        return f"- [\"{self.filename}\"](\"{self.filename.replace(" ", "%20")}\"): {self.description}\n"

    def __repr__(self):
        return self.__str__()

# Export Parameters
ProjectName = "VOL-DISP"

MainSchematicFile = "VolumetricDisplay.kicad_sch"
MainPCBFile = "VolumetricDisplay.kicad_pcb"
ReleaseNotesTemplate = "ReleaseNotesTemplate.md"

GerberLayers = "F.Cu,B.Cu,In1.Cu,In2.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts,User.1"
FabCommonLayers = "Edge.Cuts"
BOMCols = "Reference,${QUANTITY},Value,${DNP},Exclude from BOM,Exclude from Board,Footprint,Datasheet"
BOMColNames = "Reference,Count,Value,DNP,Exclude from BOM,Exclude from Board,Footprint,Datasheet"
BOMSMTCols = "Reference,${QUANTITY},Value,Footprint,Datasheet,JLCPCB Part #"
BOMSMTColNames = "Designator,Qty,Comment,Footprint,Datasheet,JLCPCB Part #"
BOMSMTExtraParams = "--exclude-dnp"
BOMGROUPBY = "Value,Footprint,JLCPCB Part #"
PNPFileColRename = {
    "Ref" : "Designator",
    "PosX" : "Mid X",
    "PosY" : "Mid Y",
    "Rot" : "Rotation",
    "Side" : "Layer"
}


ReleasesFolder = ".\\Releases"
SchematicPrefix = "SCH_"
GerbersPrefix = "CAM_"
FabPrefix = "FAB_"
StepPrefix = "STEP_"
PositionPrefix = "PNP_"
BillOfMaterialsPrefix = "BOM_"
BillOfMaterialsSMTPrefix = "BOM-JLCPCB_"


# System Parameters
KICAD_CLI_PATH = "C:\\Program Files\\KiCad\\10.0\\bin\\"
SCRIPT_VERSION_NUMBER = "alpha 1.0"
UPDATOR = "Nathan Ford"
UPDATE_DATE = "11/10/26"

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
        return False
    pathsAreValid &= os.path.exists(MainSchematicFile)
    if(not pathsAreValid):
        print("\x1B[31mCannot find schematic file \"{}\" x1B[39m".format(MainSchematicFile))
        return False
    pathsAreValid &= os.path.exists(MainPCBFile)
    if(not pathsAreValid):
        print("\x1B[31mCannot find schematic file \"{}\" x1B[39m".format(MainSchematicFile))
        return False
    return pathsAreValid

def collectRevisionInfo():
    nameIsvalid = False
    revisionName = ""
    folders = [d for d in os.listdir(ReleasesFolder) if os.path.isdir(os.path.join(ReleasesFolder, d))]
    print("\x1B[33mPrevious Revisions:\x1B[39m")
    print(folders)
    while not nameIsvalid:
        revisionName = input("\x1B[33mNew Release Name:\x1B[39m ")
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

def exportSchematic(currExportFolder, currReleaseName):
    schFile = SchematicPrefix + ProjectName + "_" + currReleaseName + ".pdf"
    schFileName = currExportFolder + "\\" + schFile
    print("\x1B[32mExporting Schematics into file [{}]\x1B[39m".format(schFileName))
    result = subprocess.run([KICAD_CLI_EXE, "sch", "export", "pdf", "-o", schFileName, 
                             MainSchematicFile], capture_output=True, text=True)
    print(result.stdout)
    return ManifestItem(schFile, "Schematic of the PCB")

def exportGerbers(currExportFolder, currReleaseName):
    camFileName = GerbersPrefix + ProjectName + "_" + currReleaseName
    camFileDir = currExportFolder + "\\" + camFileName
    print("\x1B[32mExporting Gerbers into folder [{}]\x1B[39m".format(camFileDir))
    os.mkdir(camFileDir)
    result = subprocess.run([KICAD_CLI_EXE, "pcb", "export", "gerbers", "-o", camFileDir, 
                                "-l", GerberLayers, MainPCBFile], capture_output=True, text=True)
    print(result.stdout)
    print("\x1B[32mExporting Drill Files into folder [{}]\x1B[39m".format(camFileDir))
    result = subprocess.run([KICAD_CLI_EXE, "pcb", "export", "drill", "--excellon-separate-th", "-o", camFileDir, 
                                MainPCBFile], capture_output=True, text=True)
    print(result.stdout)
    print("\x1B[32mZipping folder [{}] into file {}.zip\x1B[39m".format(camFileDir, camFileDir))
    shutil.make_archive(camFileDir, 'zip', camFileDir)
    print("\x1B[32mCleaning up Folder [{}]\x1B[39m".format(camFileDir))
    deleteDir(camFileDir)
    return ManifestItem(camFileName + ".zip", "Gerbers + Drill files")

def exportFabDocument(currExportFolder, currReleaseName):
    fabFileName = FabPrefix + ProjectName + "_" + currReleaseName + ".pdf"
    fabFilePath = currExportFolder + "\\" + fabFileName
    print("\x1B[32mExporting Fabrication Document [{}]\x1B[39m".format(fabFilePath))
    result = subprocess.run([KICAD_CLI_EXE, "pcb", "export", "pdf", "-o", fabFilePath, "--include-border-title",  
                                    "--common-layers", FabCommonLayers,"-l", GerberLayers, "--mode-multipage", MainPCBFile], capture_output=True, text=True)
    print(result.stdout)
    return ManifestItem(fabFileName, "Schematic of the PCB")

def exportStepRenders(currExportFolder, currReleaseName):
    stepFileName = StepPrefix + ProjectName + "_" + currReleaseName + ".step"
    stepFilePath = currExportFolder + "\\" + stepFileName
    print("\x1B[32mExporting 3D model [{}]\x1B[39m".format(stepFilePath))
    result = subprocess.run([KICAD_CLI_EXE, "pcb", "export", "step", "-o", stepFilePath,  
                                    MainPCBFile, "--subst-models"], capture_output=True, text=True)
    print(result.stdout)
    return ManifestItem(stepFileName, "Full 3D render of the PCB")

def generatePositionFiles(currExportFolder, currReleaseName):
    positionFileName = PositionPrefix + ProjectName + "_" + currReleaseName + ".csv"
    positionFilePath = currExportFolder + "\\" + positionFileName
    print("\x1B[32mExporting Position File [{}]\x1B[39m".format(positionFilePath))
    result = subprocess.run([KICAD_CLI_EXE, "pcb", "export", "pos", MainPCBFile, "-o", positionFilePath, "--format", "csv",
                                    "--units", "mm"], capture_output=True, text=True)
    print(result.stdout)
    if(len(PNPFileColRename) > 0):
        print("\x1B[32mRenaming Column Headers in position file\x1B[39m")
        positionFile = ""
        with open(positionFilePath, 'r') as file:
            positionFile = file.read()
        
        for key, value in PNPFileColRename.items():
            positionFile = positionFile.replace(key, value)
            print("{} -> {}".format(key, value))

        with open(positionFilePath, 'w') as file:
            file.write(positionFile)
            file.close()
    return ManifestItem(positionFileName, "Pick and place file for SMT assembly")

def generateBillOfMaterials(currExportFolder, currReleaseName):
    bomFileName = BillOfMaterialsPrefix + ProjectName + "_" + currReleaseName + ".csv"
    bomFilePath = currExportFolder + "\\" + bomFileName
    smtBomFileName = BillOfMaterialsSMTPrefix + ProjectName + "_" + currReleaseName + ".csv"
    smtBomFilePath = currExportFolder + "\\" + smtBomFileName
    print("\x1B[32mExporting Bill Of Materials [{}]\x1B[39m".format(bomFilePath))
    result = subprocess.run([KICAD_CLI_EXE, "sch", "export", "bom", MainSchematicFile, "-o", bomFilePath, "--group-by" , BOMGROUPBY,
                            "--ref-range-delimiter", "", "--fields", BOMCols, "--labels", BOMColNames], capture_output=True, text=True)
    print(result.stdout)
    print("\x1B[32mExporting SMT ASM Bill Of Materials [{}]\x1B[39m".format(bomFilePath))
    result = subprocess.run([KICAD_CLI_EXE, "sch", "export", "bom", MainSchematicFile, "-o", smtBomFilePath, "--group-by" , BOMGROUPBY,
                            "--ref-range-delimiter", "", "--fields", BOMSMTCols, "--labels", BOMSMTColNames, BOMSMTExtraParams], capture_output=True, text=True)
    print(result.stdout)
    return [ManifestItem(bomFileName, "Master Bill of Materials"), \
            ManifestItem(smtBomFileName, "Bill of Materials for SMT assembly")]

def generateReleaseNotes(currExportFolder, currReleaseName, manifest):
    releaseNotesFileName = "Release Notes.md"
    manifest.append(ManifestItem(releaseNotesFileName, "This document"))
    releaseNotesFilePath = currExportFolder + "\\" + releaseNotesFileName
    print("\x1B[32mGenerating Release Notes [{}]\x1B[39m".format(releaseNotesFilePath))
    if(not os.path.exists(ReleaseNotesTemplate)):
        print("\x1B[31mCannot find Release Notes Template \"{}\"!x1B[39m".format(ReleaseNotesTemplate))
        return False
    templateText = open(ReleaseNotesTemplate).read()
    manifestItemsStr = ""
    for item in manifest:
        manifestItemsStr += item.__str__()

    releaseNotesText = input("\x1B[32mRelease Notes: \x1B[39m");
    userName = input("\x1B[32mReleaser Name: \x1B[39m");

    templateText = templateText.format(rev=currReleaseName, date=date.today(), releaseNotes=releaseNotesText, manifest=manifestItemsStr, user=userName, projectName=ProjectName)

    releaseNotes = open(releaseNotesFilePath, 'w')
    releaseNotes.write(templateText)
    releaseNotes.close()
    

# MainProgram:

def manifestAppend(manifest, item):
    if isinstance(item, ManifestItem):
        manifest.append(item)
    elif isinstance(item, list):
        for i in item:
            if isinstance(i, ManifestItem):
                manifest.append(i)
    return manifest

def main():
    print("\x1B[32mKiCad Export Script Version: {}\x1B[39m".format(SCRIPT_VERSION_NUMBER))
    print("Created by Nathan Ford 2026")
    print("Updated by {} {}".format(UPDATOR, UPDATE_DATE))
    if(not(arePathsValid())):
        print("\x1B[32mclosing\x1B[39m")
        return ERROR_CODES.PATHS_DO_NOT_EXIST
    print("\x1B[32mPaths are valid\x1B[39m")
    createDirectory()
    
    currReleaseName = collectRevisionInfo()
    currExportFolder = createRevisionFolder(currReleaseName)
    if (currExportFolder == ""):
        return ERROR_CODES.REVISION_ALREADY_EXISTS
    manifest = []
    
    manifest = manifestAppend(manifest, exportSchematic(currExportFolder, currReleaseName))
    manifest = manifestAppend(manifest, exportGerbers(currExportFolder, currReleaseName))
    manifest = manifestAppend(manifest, exportFabDocument(currExportFolder, currReleaseName))
    manifest = manifestAppend(manifest, exportStepRenders(currExportFolder, currReleaseName))
    manifest = manifestAppend(manifest, generatePositionFiles(currExportFolder, currReleaseName))
    manifest = manifestAppend(manifest, generateBillOfMaterials(currExportFolder, currReleaseName))

    generateReleaseNotes(currExportFolder, currReleaseName, manifest)

    print("\x1B[32mExport Finished\x1B[39m")
    return ERROR_CODES.ALL_OK

if __name__ == "__main__":
    main()
from calibre.customize import InterfaceActionBase


class VCFRCalibrePlugin(InterfaceActionBase):
    name = "VCFR — Voice Command For Readest"
    description = "Open the selected EPUB in the VCFR reading companion."
    supported_platforms = ["linux"]
    author = "VCFR contributors"
    version = (0, 1, 0)
    minimum_calibre_version = (6, 0, 0)
    actual_plugin = "calibre_plugins.vcfr.ui:VCFRAction"
    type = "User Interface Action"

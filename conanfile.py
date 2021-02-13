from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class GltfSdkConan(ConanFile):
    name = "ms-gltf-sdk"
    description = "A C++ Deserializer/Serializer for glTF"
    license = "MIT"
    topics = ("conan", "gltf-sdk", "gltf", "serializer", "deserializer")
    homepage = "https://github.com/microsoft/glTF-SDK"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Windows only")

    def requirements(self):
        self.requires("rapidjson/cci.20200410")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("glTF-SDK-r" + self.version, self._source_subfolder)

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "add_subdirectory(External/RapidJSON)", "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "add_subdirectory(External/googletest)", "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "GLTFSDK", "CMakeLists.txt"),
                              "target_link_libraries(GLTFSDK\n    RapidJSON\n)", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_UNIT_TESTS"] = False
        self._cmake.definitions["ENABLE_SAMPLES"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["GLTFSDK"]

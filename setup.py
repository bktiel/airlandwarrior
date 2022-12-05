from setuptools import setup

setup(
    py_modules=['images', 'models', 'sounds', 'definitions'],
    name='airlandwarrior',
    options={
        'build_apps': {
            # Build as a GUI application
            'gui_apps': {
                'airlandwarrior': 'main.py',
            },

            "icons": {
                "*": ["images/icon_128.png", "images/icon_64.png", "images/icon_32.png"],
            },

            'platforms': ['win_amd64'],
            # Set up output logging, important for GUI apps!
            'log_filename': '$USER_APPDATA/airlandwarrior/output.log',
            'log_append': False,

            # Specify which files are included with the distribution
            'include_patterns': [
                '**/*.png',
                '**/*.jpg',
                '**/*.egg',
                '**/*.ogg',
                "**/*.bam",
                "**/*.glsl",
                "**/*.csv"
            ],

            'exclude_patterns': [
                'build',
                'src',
            ],

            # Include the OpenGL renderer and OpenAL audio plug-in
            'plugins': [
                'pandagl',
                'p3openal_audio',
            ],
        }
    }
)

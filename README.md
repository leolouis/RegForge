RegForge

A curated collection of safe, documented, and reversible Windows Registry tweaks.

What is RegForge?

RegForge is an open-source collection of Windows Registry tweaks designed to make configuration changes easier to discover, understand, apply, and reverse.

Every tweak is intended to be:

Documented

Reversible

Clearly categorized

Easy to understand

Tested before being included

Categories
Category	Description
Explorer	Windows File Explorer tweaks
Taskbar	Taskbar and Start menu configuration
Desktop	Desktop and visual settings
Privacy	Privacy-related Windows settings
Performance	System and UI performance settings
Networking	Windows networking configuration
Windows Update	Windows Update configuration
System	General Windows system settings
Repository Structure
regforge/
├── tweaks/
│   ├── explorer/
│   ├── taskbar/
│   ├── desktop/
│   ├── privacy/
│   ├── performance/
│   ├── networking/
│   ├── windows-update/
│   └── system/
├── docs/
├── profiles/
├── README.md
└── LICENSE

Using a Tweak

Open the category containing the tweak you want.

Read its README.md.

Review the registry changes before applying them.

Back up relevant registry settings when appropriate.

Run the .reg file to apply the change.

Use the provided rollback file if you want to reverse the change.

Safety

Registry changes can affect Windows configuration and behavior.

Before applying a tweak:

Read its documentation.

Understand what registry keys and values it changes.

Create an appropriate backup when necessary.

Do not apply tweaks you do not understand.

RegForge aims to provide documented and reversible changes, but users are responsible for reviewing and testing changes on their own systems.

Contributing

Contributions are welcome.

When adding a new tweak, please provide:

A descriptive name

An enable.reg file

A disable.reg rollback file

Documentation explaining the change

The affected registry hive and path

Any required permissions

Supported Windows versions, when relevant

Testing information

License

RegForge is released under the MIT License.

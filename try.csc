<?xml version='1.0' encoding='utf-8'?>
<simconf version="2023090101">
	<simulation>
		<title>My simulation</title>
		<randomseed>123456</randomseed>
		<motedelay_us>1000000</motedelay_us>
		<radiomedium>
      org.contikios.mrm.MRM
      <obstacles />
		</radiomedium>
		<events>
			<logoutput>80000</logoutput>
		</events>
		<motetype>
      org.contikios.cooja.contikimote.ContikiMoteType
      <description>Sensor Node</description>
			<source>[CONFIG_DIR]/sensor_node.c</source>
			<commands>$(MAKE) -j$(CPUS) sensor_node.cooja TARGET=cooja</commands>
			<moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
			<moteinterface>org.contikios.cooja.interfaces.Battery</moteinterface>
			<moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiVib</moteinterface>
			<moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiMoteID</moteinterface>
			<moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRS232</moteinterface>
			<moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiBeeper</moteinterface>
			<moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
			<moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRadio</moteinterface>
			<moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiButton</moteinterface>
			<moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiPIR</moteinterface>
			<moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiClock</moteinterface>
			<moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiLED</moteinterface>
			<moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiCFS</moteinterface>
			<moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiEEPROM</moteinterface>
			<moteinterface>org.contikios.cooja.interfaces.Mote2MoteRelations</moteinterface>
			<moteinterface>org.contikios.cooja.interfaces.MoteAttributes</moteinterface>
			<mote>
				<interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="468.5037251766066" y="923.2707760421541" />
				</interface_config>
				<interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>1</id>
				</interface_config>
			</mote>
			<mote>
				<interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="355.03859488017093" y="266.23151690512503" />
				</interface_config>
				<interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>2</id>
				</interface_config>
			</mote>
			<mote>
				<interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="810.8732779446331" y="1046.9101702057872" />
				</interface_config>
				<interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>3</id>
				</interface_config>
			</mote>
			<mote>
				<interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="839.8693990034033" y="753.2193934038293" />
				</interface_config>
				<interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>4</id>
				</interface_config>
			</mote>
			<mote>
				<interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="292.4666307710668" y="732.1952380377685" />
				</interface_config>
				<interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>5</id>
				</interface_config>
			</mote>
			<mote>
				<interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="601.7656744431905" y="1246.3529038851914" />
				</interface_config>
				<interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>6</id>
				</interface_config>
			</mote>
			<mote>
				<interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="397.24569379141485" y="807.2827970419955" />
				</interface_config>
				<interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>7</id>
				</interface_config>
			</mote>
			<mote>
				<interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="153.6001384982326" y="1077.977058508019" />
				</interface_config>
				<interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>8</id>
				</interface_config>
			</mote>
		</motetype>
	</simulation>
	<plugin>
    org.contikios.cooja.plugins.Visualizer
    <plugin_config>
			<moterelations>true</moterelations>
			<skin>org.contikios.cooja.plugins.skins.IDVisualizerSkin</skin>
			<skin>org.contikios.cooja.plugins.skins.TrafficVisualizerSkin</skin>
			<skin>org.contikios.mrm.MRMVisualizerSkin</skin>
			<viewport>0.5314740580389816 0.0 0.0 0.5314740580389816 37.998356682947666 -115.94969012198604</viewport>
		</plugin_config>
		<bounds x="1" y="1" height="627" width="617" z="3" />
	</plugin>
	<plugin>
    org.contikios.cooja.plugins.LogListener
    <plugin_config>
			<filter>ID</filter>
			<formatted_time />
			<coloring />
		</plugin_config>
		<bounds x="931" y="430" height="1084" width="1488" />
	</plugin>
	<plugin>
    org.contikios.cooja.plugins.Notes
    <plugin_config>
			<notes>Enter notes here</notes>
			<decorations>true</decorations>
		</plugin_config>
		<bounds x="963" y="124" height="160" width="1232" z="2" />
	</plugin>
	<plugin>
    org.contikios.cooja.plugins.ScriptRunner
    <plugin_config>
			<scriptfile>[CONFIG_DIR]/coojalogger.js</scriptfile>
			<active>true</active>
		</plugin_config>
		<bounds x="0" y="0" height="700" width="600" z="-1" minimized="true" />
	</plugin>
	<plugin>
    org.contikios.cooja.plugins.ScriptRunner
    <plugin_config>
			<scriptfile>[CONFIG_DIR]/coojalogger.js</scriptfile>
			<active>true</active>
		</plugin_config>
		<bounds x="2809" y="161" height="700" width="600" z="1" />
	</plugin>
</simconf>
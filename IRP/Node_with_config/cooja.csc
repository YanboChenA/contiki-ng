<?xml version='1.0' encoding='utf-8'?>
<simconf version="2023090101">
  <simulation>
    <title>MRM SImulation</title>
    <randomseed>generated</randomseed>
    <motedelay_us>1000000</motedelay_us>
    <radiomedium>
      org.contikios.mrm.MRM
      <bg_noise_var value="2.0" />
      <bg_noise_mean value="-85" />
      <obstacles />
    </radiomedium>
    <events>
      <logoutput>80000</logoutput>
    </events>
    <motetype>
      org.contikios.cooja.contikimote.ContikiMoteType
      <description>sensor_node</description>
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
          <pos x="0.0" y="0.0" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>1</id>
        </interface_config>
      </mote>
    <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-27.672101893540457" y="-33.41266093814552" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>2</id>
        </interface_config>
      </mote>
    <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-73.08886873877181" y="-34.7266680682274" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>3</id>
        </interface_config>
      </mote>
    <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-34.048442060499355" y="-69.36267516616878" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>4</id>
        </interface_config>
      </mote>
    <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="19.330163392067874" y="35.07350633229714" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>5</id>
        </interface_config>
      </mote>
    <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="39.520260231599394" y="76.80755153654516" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>6</id>
        </interface_config>
      </mote>
    <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-38.31103884778002" y="6.210764845557321" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>7</id>
        </interface_config>
      </mote>
    <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-70.35154732380519" y="-74.54702663682568" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>8</id>
        </interface_config>
      </mote>
    <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="87.94529009917574" y="76.13918028405601" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>9</id>
        </interface_config>
      </mote>
    <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="39.90659477943859" y="-0.15824997693138698" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>10</id>
        </interface_config>
      </mote>
    <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-6.5078487151574365" y="93.44606924329412" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>11</id>
        </interface_config>
      </mote>
    </motetype>
  </simulation>
  <plugin>
    org.contikios.cooja.plugins.Visualizer
    <plugin_config>
      <moterelations>true</moterelations>
      <skin>org.contikios.cooja.plugins.skins.IDVisualizerSkin</skin>
      <skin>org.contikios.cooja.plugins.skins.GridVisualizerSkin</skin>
      <skin>org.contikios.cooja.plugins.skins.TrafficVisualizerSkin</skin>
      <skin>org.contikios.mrm.MRMVisualizerSkin</skin>
      <viewport>0.9090909090909091 0.0 0.0 0.9090909090909091 194.0 173.0</viewport>
    </plugin_config>
    <bounds x="1" y="1" height="400" width="400" z="1" />
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.LogListener
    <plugin_config>
      <filter />
      <formatted_time />
      <coloring />
    </plugin_config>
    <bounds x="400" y="160" height="240" width="1232" z="4" />
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.TimeLine
    <plugin_config>
      <mote>0</mote>
      <showRadioRXTX />
      <showRadioHW />
      <showLEDs />
      <zoomfactor>500.0</zoomfactor>
    </plugin_config>
    <bounds x="0" y="793" height="166" width="1632" z="3" />
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.Notes
    <plugin_config>
      <notes>Enter notes here</notes>
      <decorations>true</decorations>
    </plugin_config>
    <bounds x="400" y="0" height="160" width="1232" z="2" />
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.ScriptRunner
    <plugin_config>
      <scriptfile>[CONFIG_DIR]/coojalogger.js</scriptfile>
      <active>true</active>
    </plugin_config>
    <bounds x="635" y="420" height="700" width="600" />
  </plugin>
</simconf>
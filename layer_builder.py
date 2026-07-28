# -*- coding: utf-8 -*-
import json
import os

from qgis.core import (
    QgsVectorLayer,
    QgsProject,
    QgsAction,
    QgsHtmlAnnotation,
)

# ── QML style embedded as string ─────────────────────────────────────────────
# Two-layer SVG marker: Arrow_06 (rotated by azimuth) + camera.svg on top
# Labels: substr(filepath, 50, 8)
# MapTip: inline photo thumbnail
QML_STYLE = """<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="0" labelsEnabled="1" simplifyDrawingHints="0" readOnly="0"
      simplifyAlgorithm="0" version="3.22.0-Białowieża"
      hasScaleBasedVisibilityFlag="0" minScale="100000000"
      simplifyDrawingTol="1" symbologyReferenceScale="-1"
      styleCategories="AllStyleCategories" simplifyLocal="1" simplifyMaxScale="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <renderer-v2 symbollevels="0" forceraster="0" enableorderby="0"
               type="singleSymbol" referencescale="-1">
    <symbols>
      <symbol force_rhr="0" name="0" type="marker" alpha="1" clip_to_extent="1">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SvgMarker" locked="0">
          <Option type="Map">
            <Option value="0" name="angle" type="QString"/>
            <Option value="255,0,0,255" name="color" type="QString"/>
            <Option value="0" name="fixedAspectRatio" type="QString"/>
            <Option value="1" name="horizontal_anchor_point" type="QString"/>
            <Option value="arrows/Arrow_06.svg" name="name" type="QString"/>
            <Option value="0.00000000000000006,-3.00000000000000044" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="35,35,35,255" name="outline_color" type="QString"/>
            <Option value="0" name="outline_width" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
            <Option value="MM" name="outline_width_unit" type="QString"/>
            <Option name="parameters"/>
            <Option value="diameter" name="scale_method" type="QString"/>
            <Option value="6" name="size" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
            <Option value="MM" name="size_unit" type="QString"/>
            <Option value="1" name="vertical_anchor_point" type="QString"/>
          </Option>
          <prop v="0" k="angle"/>
          <prop v="255,0,0,255" k="color"/>
          <prop v="0" k="fixedAspectRatio"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="arrows/Arrow_06.svg" k="name"/>
          <prop v="0.00000000000000006,-3.00000000000000044" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="" k="parameters"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="6" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties" type="Map">
                <Option name="angle" type="Map">
                  <Option value="true" name="active" type="bool"/>
                  <Option value="azimuth" name="field" type="QString"/>
                  <Option value="2" name="type" type="int"/>
                </Option>
              </Option>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer pass="0" enabled="1" class="SvgMarker" locked="0">
          <Option type="Map">
            <Option value="0" name="angle" type="QString"/>
            <Option value="0,0,0,255" name="color" type="QString"/>
            <Option value="0" name="fixedAspectRatio" type="QString"/>
            <Option value="1" name="horizontal_anchor_point" type="QString"/>
            <Option value="gpsicons/camera.svg" name="name" type="QString"/>
            <Option value="0,0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="255,255,255,255" name="outline_color" type="QString"/>
            <Option value="0" name="outline_width" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
            <Option value="MM" name="outline_width_unit" type="QString"/>
            <Option name="parameters"/>
            <Option value="diameter" name="scale_method" type="QString"/>
            <Option value="4" name="size" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
            <Option value="MM" name="size_unit" type="QString"/>
            <Option value="1" name="vertical_anchor_point" type="QString"/>
          </Option>
          <prop v="0" k="angle"/>
          <prop v="0,0,0,255" k="color"/>
          <prop v="0" k="fixedAspectRatio"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="gpsicons/camera.svg" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="255,255,255,255" k="outline_color"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="" k="parameters"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="4" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style fieldName="&quot;filename&quot;"
        capitalization="0" namedStyle="Normal" fontSize="10"
        fontSizeMapUnitScale="3x:0,0,0,0,0,0" isExpression="0"
        fontStrikeout="0" previewBkgrdColor="255,255,255,255"
        fontItalic="0" legendString="Aa" fontUnderline="0"
        fontFamily="Arial" useSubstitutions="0" fontSizeUnit="Point"
        fontKerning="1" fontWeight="50" allowHtml="0"
        textColor="50,50,50,255" fontWordSpacing="0" textOpacity="1"
        blendMode="0" textOrientation="horizontal" fontLetterSpacing="0"
        multilineHeight="1">
        <families/>
        <text-buffer bufferBlendMode="0" bufferNoFill="1"
          bufferSizeUnits="MM" bufferColor="250,250,250,255"
          bufferDraw="1" bufferSize="1" bufferOpacity="1"
          bufferJoinStyle="128"
          bufferSizeMapUnitScale="3x:0,0,0,0,0,0"/>
        <text-mask maskEnabled="0" maskOpacity="1" maskJoinStyle="128"
          maskSizeUnits="MM" maskType="0" maskedSymbolLayers=""
          maskSize="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0"/>
        <background shapeDraw="0"/>
        <shadow shadowDraw="0"/>
        <dd_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format reverseDirectionSymbol="0" formatNumbers="0"
        decimals="3" rightDirectionSymbol="&gt;" wrapChar=""
        autoWrapLength="0" addDirectionSymbol="0" useMaxLineLengthForAutoWrap="1"
        multilineAlign="3" leftDirectionSymbol="&lt;" plussign="0"
        placeDirectionSymbol="0"/>
      <placement geometryGeneratorEnabled="0" overrunDistance="0"
        rotationUnit="AngleDegrees" layerType="PointGeometry"
        centroidInside="0" geometryGeneratorType="PointGeometry"
        overrunDistanceUnit="MM" xOffset="0" dist="1" distUnits="MM"
        labelOffsetMapUnitScale="3x:0,0,0,0,0,0" fitInPolygonOnly="0"
        distMapUnitScale="3x:0,0,0,0,0,0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0"
        repeatDistanceUnits="MM" preserveRotation="1"
        repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" repeatDistance="0"
        placement="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR"
        quadOffset="4" yOffset="0" maxCurvedCharAngleIn="25"
        maxCurvedCharAngleOut="-25" priority="5" offsetType="0"
        offsetUnits="MM" rotationAngle="0" geometryGenerator=""
        polygonPlacementFlags="2" centroidWhole="0" overlapHandling="PreventOverlap"
        allowDegraded="0"/>
      <rendering fontMinPixelSize="3" limitNumLabels="0" obstacleFactor="1"
        maxNumLabels="2000" fontMaxPixelSize="10000" minFeatureSize="0"
        scaleMin="0" obstacle="1" fontLimitPixelSize="0" scaleVisibility="0"
        scaleMax="0" upsidedownLabels="0" mergeLines="0"
        unplacedVisibility="0" obstacleType="1" zIndex="0"
        drawLabels="1" labelPerPart="0"/>
      <dd_properties>
        <Option type="Map">
          <Option value="" name="name" type="QString"/>
          <Option name="properties"/>
          <Option value="collection" name="type" type="QString"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option value="pole_of_inaccessibility" name="anchorPoint" type="QString"/>
          <Option value="0" name="blendMode" type="int"/>
          <Option name="ddProperties" type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
          <Option value="false" name="drawToAllParts" type="bool"/>
          <Option value="false" name="enabled" type="bool"/>
          <Option value="point_on_exterior" name="labelAnchorPoint" type="QString"/>
          <Option value="&lt;symbol force_rhr=&quot;0&quot; name=&quot;arrow&quot; type=&quot;line&quot; alpha=&quot;1&quot; clip_to_extent=&quot;1&quot;/>" name="lineSymbol" type="QString"/>
          <Option value="0" name="minLength" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="minLengthMapUnitScale" type="QString"/>
          <Option value="MM" name="minLengthUnit" type="QString"/>
          <Option value="0" name="offsetFromAnchor" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="offsetFromAnchorMapUnitScale" type="QString"/>
          <Option value="MM" name="offsetFromAnchorUnit" type="QString"/>
          <Option value="0" name="offsetFromLabel" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="offsetFromLabelMapUnitScale" type="QString"/>
          <Option value="MM" name="offsetFromLabelUnit" type="QString"/>
        </Option>
      </callout>
    </settings>
  </labeling>
  <fieldConfiguration>
    <field name="filepath" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
    <field name="filename" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
    <field name="longitude" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
    <field name="latitude" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
    <field name="altitude" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
    <field name="north" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
    <field name="azimuth" configurationFlags="None">
      <editWidget type="Range"><config><Option/></config></editWidget>
    </field>
    <field name="gimbal_pitch" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
    <field name="gps_date" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
    <field name="img_date" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
    <field name="flight_yaw" configurationFlags="None">
      <editWidget type="Range"><config><Option/></config></editWidget>
    </field>
    <field name="source" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
    <field name="rtk_flag" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
    <field name="rtk_std_lon" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
    <field name="rtk_std_lat" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
    <field name="rtk_std_hgt" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
    <field name="speed_x" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
    <field name="speed_y" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
    <field name="speed_z" configurationFlags="None">
      <editWidget type="TextEdit"><config><Option/></config></editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0"  field="filepath"    name=""/>
    <alias index="1"  field="filename"    name=""/>
    <alias index="2"  field="longitude"   name=""/>
    <alias index="3"  field="latitude"    name=""/>
    <alias index="4"  field="altitude"    name="wys. abs. [m]"/>
    <alias index="5"  field="north"       name=""/>
    <alias index="6"  field="azimuth"     name="azymut [°]"/>
    <alias index="7"  field="gimbal_pitch" name="pochylenie [°]"/>
    <alias index="8"  field="flight_yaw"  name="kier. lotu [°]"/>
    <alias index="8"  field="gps_date"    name="data GPS"/>
    <alias index="9"  field="img_date"    name="data zdjęcia"/>
    <alias index="10" field="source"      name="źródło"/>
    <alias index="11" field="rtk_flag"    name="RTK flag"/>
    <alias index="12" field="rtk_std_lon" name="RTK σLon [m]"/>
    <alias index="13" field="rtk_std_lat" name="RTK σLat [m]"/>
    <alias index="14" field="rtk_std_hgt" name="RTK σHgt [m]"/>
    <alias index="15" field="speed_x"     name="Vx [m/s]"/>
    <alias index="16" field="speed_y"     name="Vy [m/s]"/>
    <alias index="17" field="speed_z"     name="Vz [m/s]"/>
  </aliases>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
    <actionsetting action="[%filepath%]" notificationMessage=""
      name="Open file" icon="" id="{bb28fa30-3c43-4408-a6dc-ce5ff67559f9}"
      isEnabledOnlyWhenEditable="0" type="5" shortTitle="" capture="0">
      <actionScope id="Feature"/>
      <actionScope id="Canvas"/>
      <actionScope id="Field"/>
    </actionsetting>
  </attributeactions>
  <mapTip>[% CASE
  WHEN left("filepath", 1) = '/' THEN concat('&lt;img src="file://', "filepath", '" width=200 height=200/>')
  ELSE concat('&lt;img src="file:///', "filepath", '" width=200 height=200/>')
END %]</mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>"""


def build_geojson(photo_data_list):
    """Convert list of photo dicts to GeoJSON FeatureCollection."""
    features = []
    for d in photo_data_list:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [d['longitude'], d['latitude']]
            },
            "properties": {
                "filepath":    d.get('filepath'),
                "filename":    d.get('filename'),
                "longitude":   d.get('longitude'),
                "latitude":    d.get('latitude'),
                "altitude":    d.get('altitude'),
                "north":       d.get('north'),
                "azimuth":     d.get('azimuth'),
                "gimbal_pitch": d.get('gimbal_pitch'),
                "flight_yaw":  d.get('flight_yaw'),
                "gps_date":    d.get('gps_date'),
                "img_date":    d.get('img_date'),
                "source":      d.get('source'),
                "rtk_flag":    d.get('rtk_flag'),
                "rtk_std_lon": d.get('rtk_std_lon'),
                "rtk_std_lat": d.get('rtk_std_lat'),
                "rtk_std_hgt": d.get('rtk_std_hgt'),
                "speed_x":     d.get('speed_x'),
                "speed_y":     d.get('speed_y'),
                "speed_z":     d.get('speed_z'),
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
        },
        "features": features
    }


def save_and_load_layer(photo_data_list, output_path, layer_name="photos"):
    """
    Write GeoJSON file and add styled layer to QGIS project.
    Returns the QgsVectorLayer or None on failure.
    """
    if not photo_data_list:
        return None

    geojson = build_geojson(photo_data_list)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    layer = QgsVectorLayer(output_path, layer_name, 'ogr')
    if not layer.isValid():
        return None

    # Force field index rebuild before applying QML style
    # This prevents labels not appearing until user manually re-selects the field
    layer.dataProvider().reloadData()
    layer.updateFields()

    # Write QML and apply style
    qml_path = output_path.replace('.geojson', '.qml')
    with open(qml_path, 'w', encoding='utf-8') as f:
        f.write(QML_STYLE)

    layer.loadNamedStyle(qml_path)
    layer.triggerRepaint()

    QgsProject.instance().addMapLayer(layer)
    return layer

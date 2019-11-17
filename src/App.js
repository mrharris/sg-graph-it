import React from 'react';
import * as go from 'gojs';
import {ReactDiagram} from 'gojs-react';

import './App.css';  // contains .diagram-component CSS


/**
 * This function is responsible for setting up the diagram's initial properties and any templates.
 */
function initDiagram() {

    const $ = go.GraphObject.make;
    const myDiagram =
        $(go.Diagram,
            {
                model: $(go.GraphLinksModel,
                {
                    linkFromPortIdProperty: "fromPort",
                }),
                "undoManager.isEnabled": true,
                "toolManager.mouseWheelBehavior": go.ToolManager.WheelZoom,
                "initialAutoScale": go.Diagram.Uniform,
                "layout": $(go.LayeredDigraphLayout, {
                                direction: 270,
                                layerSpacing: 35
                            }),
            });


    // This template is a Panel that is used to represent each item in a Panel.itemArray.
    // The Panel is data bound to the item object.
    let fieldTemplate =
        $(go.Panel, "TableRow",  // this Panel is a row in the containing Table
            new go.Binding("portId", "field"),  // this Panel is a "port"
            {
                fromSpot: go.Spot.Right,  // links only go from the right side to the left side
                toSpot: go.Spot.Left,
                maxSize: new go.Size(125, 12)
            },
            $(go.Shape, // icon
                {
                    width: 12, height: 12, column: 0, strokeWidth: 2, margin: 4, fill: "#FFB900", figure: "Diamond",
                }),
            $(go.TextBlock, // field
                {
                    margin: new go.Margin(0, 5), column: 1, font: "bold 13px sans-serif",
                    alignment: go.Spot.Left,
                },
                new go.Binding("text", "field")),
            $(go.TextBlock, // value
                {margin: new go.Margin(0, 5), column: 2, font: "13px sans-serif", alignment: go.Spot.Left},
                new go.Binding("text", "value"))
        );

    // This template represents a whole "record".
    myDiagram.nodeTemplate =
        $(go.Node, "Auto",
            {deletable: false},
            // this rectangular shape surrounds the content of the node
            $(go.Shape, {fill: "#c4c4c4"}),
            // the content consists of a header and a list of items
            $(go.Panel, "Vertical",
                // this is the header for the whole node
                $(go.Panel, "Auto",
                    {stretch: go.GraphObject.Horizontal},  // as wide as the whole node
                    // header background
                    $(go.Shape, {fill: "#1570A6", stroke: null}),
                    // entity name
                    $(go.TextBlock,
                        {
                            alignment: go.Spot.Left,
                            margin: 3,
                            stroke: "white",
                            font: "bold 12pt sans-serif"
                        },
                        new go.Binding("text", "name")
                    ),
                    // entity type
                    $(go.TextBlock,
                        {
                            alignment: go.Spot.Right,
                            margin: 3,
                            stroke: "#c4c4c4",
                            font: "bold 12pt sans-serif"
                        },
                        new go.Binding("text", "type")
                    ),
                ),
                $(go.Picture, {
                    name: "Picture",
                    desiredSize: new go.Size(250, 140),
                    margin: new go.Margin(4, 4, 4, 4),
                    imageStretch: go.GraphObject.UniformToFill,
                },
                    new go.Binding("source", "image"),
                ),
                // this Panel holds a Panel for each item object in the itemArray;
                // each item Panel is defined by the itemTemplate to be a TableRow in this Table
                $(go.Panel, "Table",
                    {
                        padding: 2,
                        minSize: new go.Size(100, 10),
                        defaultStretch: go.GraphObject.Horizontal,
                        itemTemplate: fieldTemplate
                    },
                    new go.Binding("itemArray", "fields")
                )  // end Table Panel of items
            )  // end Vertical Panel
        );  // end Node

    myDiagram.linkTemplate =
        $(go.Link, go.Link.Bezier,
            {deletable: false},
            $(go.Shape, {strokeWidth: 1.5}),
            $(go.Shape, {toArrow: "Standard"})
        );

    myDiagram.groupTemplate =
    $(go.Group, "Auto",
      // { layout: $(go.TreeLayout) },
      $(go.Shape, "Rectangle", { fill: "rgba(255,180,0,0.35)", stroke: "darkorange" }),
      $(go.Panel, "Table",
        { margin: 0.5 },  // avoid overlapping border with table contents
        $(go.RowColumnDefinition, { row: 0, background: "white" }),  // header is white
        $("SubGraphExpanderButton", { row: 0, column: 0, margin: 3 }),
        $(go.TextBlock,  // title is centered in header
          { row: 0, column: 1, font: "bold 14px Sans-Serif", stroke: "darkorange",
            textAlign: "center", stretch: go.GraphObject.Horizontal },
          new go.Binding("text")),
        $(go.Placeholder,  // becomes zero-sized when Group.isSubGraphExpanded is false
          { row: 1, columnSpan: 2, padding: 50, alignment: go.Spot.TopLeft },
          new go.Binding("padding", "isSubGraphExpanded",
                         function(exp) { return exp ? 10 : 0; } ).ofObject())
      )
    );

    return myDiagram;
}

// render function...
function App() {
    // Using html5 "data-attributes" like this is probably not very
    // "react-onic" :( Maybe this should use props?
    // I don't know why i need to JSON parse twice..
    let root = document.querySelector('#root');
    let data = JSON.parse(JSON.parse(root.dataset.graph));
    return (
        <div>
            <ReactDiagram
                initDiagram={initDiagram}
                divClassName='diagram-component'
                nodeDataArray={data.nodes}
                linkDataArray={data.links}
            />
        </div>
    );
}

export default App;

# Architecture diagrams

## Overview

The architecture diagrams in this directory are designed using the [C4 model](https://c4model.com) for visualising software architecture.

## Container workflow

### Design time

The msc-wis2node component uses MSC discovery metadata Metadata Control Files](https://geopython.github.io/pygeometa/reference/mcf) (managed internally)
to build a table for runtime handling and publishing of MSC data to WIS2.

### Run time

The msc-wis2node component provides the following runtime workflow:

- connects to [MSC Datamart notification service](https://eccc-msc.github.io/open-data/msc-datamart/readme_en/), subscribed to all notifications
- on data notification:
  - determine the associated MSC WCMP2 metadata and WIS2 topic
  - construct and publish a WIS2 Notification Message to the MSC WIS2 Node broker using the associated topic


## Management of diagrams

The diagrams are saved as an editable `.png` file, for easy default viewing on GitHub, showing the last active diagram when saved. Any PNG
viewer will also render the diagram in the same way.

The diagrams can be updated using [diagrams.net](https://diagrams.net) in the following manner:

- open files on this GitHub repository directly in diagrams.net
- clone this repository, edit/save using the diagrams.net desktop application ([download](https://github.com/jgraph/drawio-desktop/releases)), and commit/push files to GitHub

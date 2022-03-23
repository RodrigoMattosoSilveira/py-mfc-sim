# py-mfc-sim
An MFC simulation using SimPy

# Business Domain
## Glossary
* **carrier**: __**i**__) noun, a `DSP` provider that has its own fleet, and infrastructure to manage it;
* **carry bundle**: __**i**__) noun, number of order items to carry when building / take down an order kit;
* **courier**: __**i**__) noun, a `DSP` provider that has its own vehicle and depends on a platform to service `orders`;
* **delivery area**: __**i**__) noun, a warehouse location where a `PPP` places packed orders for delivery;
* **DSP**: __**i**__) acronym 1. Delivery Service provider, can be `carrier` or `courier`;
* **inventory slot**: __**i**__) noun, a warehouse location where a ``SKU` is located;
* **product**: __**i**__) noun, a physical instance of a `SKU`, a.k.a. `inventory item`;
* **label area**: __**i**__) noun, a warehouse location where a `PPP` labels orders bags or boxes;
* **label resource**: __**i**__) noun, an printer label to identify an `order parcel`;
* **order**: __**i**__) noun, a document describing one of more products purchased by an Ohi brand's customer and which Ohi will deliver in its entirety; 
* **order area**: __**i**__) noun, a warehouse location where a `PPP` selects their next order fulfilling mission;
* **orders bags**: __**i**__) noun, containers used to pack small `rush` / `same day` orders;  `orders bas` are  plentiful and easy to find around the warehouse;
* **orders boxes**: __**i**__) noun, containers used to pack larger `next day` / `nationwide` orders; `orders boxes` are not plentiful and hard to find around the warehouse;
* **order item**: __**i**__) noun, same as `order line item`; __**ii**__) plural, count of an order's invidual produts;
* **order kit**: __**i**__) noun, a collection of multiple inventory items required to fulfill an order;
* **oder kit location**: __**i**__) noun,  a pack area location to assemble a multi item order
* **order line item**: __**i**__) noun, a brand's product purchased by its customer, and included in an order for Ohi to deliver; 
* **order tablet**: __**i**__) noun, a device the `PPP` uses to get the next order fulfillment, and to update their order fulfillment tasks;
* **outbound box shelf**: __**i**__) noun, a pack area location to assemble a multi item order;
* **OOL**: __**i**__) acronym, Out of label;
* **OOP**: __**i**__) acronym, Out of packing resource;
* **OOS**: __**i**__) acronym, Out of stock;
* **pack area**: __**i**__) noun, a warehouse location where a `PPP` packs the inventory item(s) required to fulfill an order;
* **pack location**: __**i**__) noun, a location within the `pack area` where a `PPP` packs a specific `order`;
* **pack resource**: __**i**__) noun, an `order bag` or an `order box`;
* **pallet**: __**i**__) noun, TBD;
* **parcel**: __**i**__) noun, container, an `order bag` or an `order box`, with order items;
* **pick area**: __**i**__) noun, a warehouse location where a `PPP` picks the  inventory item(s) required to fulfill an order;
* **pick slot**: __**i**__) noun, a pick are location to pick an inventory item to fulfill an order line item
* **PnP**: __**i**__) acronym, Pick and Pack process, a series of steps to fulfill `orders`;
* **PPP** __**i**__) acronym Pick and Pack Partner, an individual who executes the `PnP` process;
* **SKU** __**i**__) acronym, Stock Keeping Unit, it is a number (usually eight alphanumeric digits) assigned to products to keep track of stock levels internally; the same product, but with a different color, or size, will have its own unique SKU number.
* **stage area** __**i**__) noun, a warehouse location where a `PPP` uses to build `order kits`; we will use a `pack location` as `stage areas`;

## The PPP workflows
A `PPP` has the following workflows:
* 70% PnP;
* 15% Receiving and Cleaning;
*  5% Cycle Count;
*  5% Parcel Level Scanning (TRIPS);
A `PPP` mission is to fulfill `orders`. The `PPP` executes its mission through repeated executions of the `PnP` cycle; they work `SHIFT_WORK_DURATION` hours, performs `PnP tasks`, takes periodic `shift breaks` and `hourly breaks` in between ` their PnP` work.

#### Sunny Day
* check in 
  * arrives at the check in area 
  * If not working, get a PPP tally
  * If working, and has an outstanding order tally
    * requests order tablet, and wait
    * record previous order results
* rest
  * arrives at rest area
  * rest for the amount of time, 0 if not
* receive and clean
  * 15%
cycle count
  * 5%
* parcel level scanning
  * 5%
* get next order
  * arrives at the order area
  * requests order tablet, waits for tablet
  * requests next order, waits for the next order
  * gets, reads, and memorizes the order
  * decides how many containers for the order
  * retrieves the order's container(s), they are always available
    * 1 bags for rush / same day
    * 1+ boxes for next day / national (1 container per 6 eaches)
    * PPP aborts order fulfillment when OOP
* pick an order
  * walks to pick area
  * Repeat until picked items == order items
    * Repeat until items in container == items per container
      * picks the next order item
        * if OOS condition arises
          * puts away the items in box at hand
          * puts away items in outbound shelf box(es) - pack area
          * aborts order fulfillment
    * takes packing container, bo, to an outbound box shelf location (∞)
* pack an order
  * pack the parcels
* label an order
  * walks to the label area
  * retrieves the label material
    * If OOL
      * puts away items in outbound shelf box(es) - pack area
      *  aborts order fulfillment
  * wait for label printer
  * labels the parcel(s)
* set an order for delivery
  * walks to the delivery area
  * retrieves delivery fridge space, for some parcels
    * if OOF
      * puts away items in outbound shelf box(es) - pack area
      * aborts order fulfillment
  * places the parcel(s) in delivery area
  * return to check in area

### Exception handling
* put-away order kit
  * for each product in hand,if any
    * walt to pick slot
    * put product away
  * walk to order kit location
    * for each order carry bundle
      * pick a carry bundle
      * carry bundle to pick area
      * For each product in carry bundle
        * walk to product pick slot location
        * put away product
    * return to check in area, from pick area after putting away all order items
* put-away order parcel(s)
  * for each order parcel(s)
    * for each order carry bundle
      * pick a carry bundle
      * carry bundle to pick area
      * For each product in carry bundle
        * walk to product pick slot location
        * put away product
    * return to check in area, from pick area after putting away all order items


# Simulation
We will simulate multiple `PPP` executing their missions concurrently; they will work `SHIFT_WORK_DURATION` hours, performing their `PnP tasks`, takes periodic `shift breaks` and `hourly breaks` in between ` their PnP` work.

We will simulate `PnP tasks` by randomizing the time, in simulation ticks equivalent to seconds. For example, we simulate a `PPP` walking between two points in the warehouse by picking a rondom number from a normal distribution with a reaosble average to walk the distance and a narrow standard deviation.

We will simulate scarce resources by waiting for the resource to become available, as for instance the order tablet, or by aborting the `PnP` mission, as for instance when packing resources are not available.

Following we describe how use SimPy's `events`, `resources` and `process` to model our MFCs.

## Events
We will use events to simulate actual `PnP` activities, and capture them as the time to execute these activities. There are few distinct distributions:
### Absolute
These are configurable values used as is. For example, the shift duration in parameters.SHIFT_WORK_DURATION

### Normal
These are configurable values used to generate a random value based on a normal distribution around a mean with a narrow standard deviation. 

For example, we calculate the time to walk to the pick area, by selecting a random number from a normal distribution between
* parameters.TIME_TO_WALK_TO_PICK_STATION_MIN, and 
* parameters.TIME_TO_WALK_TO_PICK_STATION_MAX

### Arbitrary
These are configurable values used to generate a random value based on a arbitrary distribution around certain known values. 

For example, we estimate whether a product is available using an arbitrary probability that the probability that a product will be available to be
* parameters.INVENTORY_AVAILABILITY_PROBABILITY, based on today's inventory accuracy.

## Resources
Resources are things that `processes` use to execute a task. We will model two types of resources:
* **Wait** - the `PPP` waits until this resource is available;
* **Abort** - `PPP` aborts the `PnP` cycle if this resource is unavailable;

### Wait
* **order tablet** There is one per warehouse; 
* **stage area** There are `STAGE_AREAS` per warehouse; 
* **label printer** There `LABEL_PRINTERS` per warehouse;

### Abort
* **product** There is a `INVENTORY_AVAILABILITY_PROBABILITY` probability that this resource is available;
* **bag** There is a `BAG_AVAILABILITY_PROBABILITY` probability that this resource is available;
* **box** There is a `BOX_AVAILABILITY_PROBABILITY` probability that this resource is available;
* **label** There is a `LABEL_AVAILABILITY_PROBABILITY` probability that this resource is available;
* **delivery fridge** There is a `DELIVERY_FRIDGE_AVAILABILITY_PROBABILITY` probability that this resource is available;

## Processes
We describe the the `PnP`above, on the `The Pick and Pack Cycle` section.
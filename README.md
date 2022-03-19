# py-mfc-sim
An MFC simulation using SimPy

# Business Domain
## Glossary
* **carrier**: __**i**__) noun, a `DSP` provider that has its own fleet, and infrastructure to manage it;
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
* **order item**: __**i**__) noun, same as `order line item`;
* **order kit**: __**i**__) noun, a collection of multiple inventory items required to fulfill an order;
* **order line item**: __**i**__) noun, a brand's product purchased by its customer, and included in an order for Ohi to deliver; 
* **order tablet**: __**i**__) noun, a device the `PPP` uses to get the next order fulfillment, and to update their order fulfillment tasks;
* **pack area**: __**i**__) noun, a warehouse location where a `PPP` packs the inventory item(s) required to fulfill an order;
* **pack location**: __**i**__) noun, a location within the `pack area` where a `PPP` packs a specific `order`;
* **pack resource**: __**i**__) noun, an `order bag` or an `order box`;
* **parcel**: __**i**__) noun, container with order items, with an `order bag` or an `order box`;
* **pick area**: __**i**__) noun, a warehouse location where a `PPP` picks the  inventory item(s) required to fulfill an order;
* **pick slot**: __**i**__) noun, a pick are location to pick an inventory item to fulfill an order line item
* **PnP**: __**i**__) acronym, Pick and Pack process, a series of steps to fulfill `orders`;
* **PPP** __**i**__) acronym Pick and Pack Partner, an individual who executes the `PnP` process;
* **SKU** __**i**__) acronym, Stock Keeping Unit, it is a number (usually eight alphanumeric digits) assigned to products to keep track of stock levels internally; the same product, but with a different color, or size, will have its own unique SKU number.
* **stage area** __**i**__) noun, a warehouse location where a `PPP` uses to build `order kits`; we will use a `pack location` as `stage areas`;

## The Pick and Pack Cycle
A `PPP` mission is to fulfill `orders`. The `PPP` executes its mission through repeated executions of the `PnP` cycle; they work `SHIFT_WORK_DURATION` hours, performs `PnP tasks`, takes periodic `shift breaks` and `hourly breaks` in between ` their PnP` work.

The `PnP` cycle consists of:
* order area
  * walks to the order area
  * requests order tablet
  * records previous order results
  * takes a shift or hour break
  * requests order tablet
  * requests next order
  * waits for the next order
  * gets, reads, and memorizes the order
* pick area
  * walks to pick area
  * Repeat until picking all order items
  * walks to product(s) pick slot
  * picks product(s)
    * Abandon current PnP cycle in case they cannot find product(s)
      * restore product(s) to pick area
      * returns to order area
  * walks to the stage area
  * wait for stage area
  * adds product(s) to kit
* pack area
  * retrieves pack resources
    * Abandon current PnP cycle in case they cannot retrieve pack resources
      * restore product(s) to pick area
      * returns to order area
  * pack the parcels
* label area
  * walks to the label area
  * retrieves the label material
    * Abandon current PnP cycle in case they cannot retrieve the label material
      * restore product(s) to pick area
      * returns to order area
  * wait for label printer
  * labels the parcel
* delivery area
  * walks to the delivery area
  * retrieves delivery fridge space, for some parcels
  * Abandon current PnP cycle in case they cannot retrieve delivery fridge space
    * restore product(s) to pick area
    * returns to order area
  * places the parcel(s) in delivery area
  * walks to the order area

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
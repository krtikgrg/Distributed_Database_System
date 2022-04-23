## Phase 2 Changes
1. Changes in Catalog
    1. Structure of Horzontal_Fragments changed
    1. Structure of Derived_Horizontal_Fragments changed
1. Changes in Fragmentation
    1. Order_Items table is now fragmented too
    1. It is derived horizontally fragmented using the horizonatal fragments of Food_Items table
    1. Subsequently Order table is derived horizontally fragmented using fragments of Order_Items table
1. The corresponding changes to allocation table has also been made.
    1. Well not changes to be exact.
    1. Structure is still the same.
    1. But new entries for the new made fragments are added.

## Phase 3 Changes
1. There are some changes to the catalog which we are mentioning right away, but these will be brought into effect after Phase 2 evaluation.
1. The changes are
    1. Renaming of 'User' relation to 'Users'
    1. Column 'Type' of 'Food_Item' relation is renamed to 'Item_Type'
    1. Column 'Category' of 'Food_Item' relation is renamed to 'Item_Category'
    1. Renaming of 'Order' relation to 'Orders'
    1. All the above changes are also applicable to their respective fragments appropriately.
1. Above changes were necessary as the original Application schema contained some names which were actually SQL keywords and were causing problems in the execution of the query.
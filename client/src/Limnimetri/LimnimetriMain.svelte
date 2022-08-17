<script>
    import {mobileMode} from "../Stores/store";
    import {
        Tile,
        Button,
        Search,
        Dropdown,
        TileGroup,
        SkeletonPlaceholder, ButtonSet, RadioTile, RadioButtonGroup, DataTableSkeleton, DropdownSkeleton
    } from "carbon-components-svelte";
    import {Add} from "carbon-icons-svelte";
</script>


{#if $mobileMode === true}
    <Tile>
        <div className="bx--data-table-header">
            <div className="content">
                <div>
                    <h4 className="bx--data-table-header__title">Limnimetri</h4>
                    <p className="bx--data-table-header__description">Tutti i Limnimetri.</p>
                </div>
                <div className="center">
                    <Button icon={Add} skeleton size="field"/>
                </div>
            </div>
        </div>
        <br>

        <br>
        <Search skeleton/>
        <DropdownSkeleton/>
    </Tile>
    <br>
    <TileGroup>
        <SkeletonPlaceholder style="height: 10rem; width: 100%;"/>
        <br>
        <SkeletonPlaceholder style="height: 10rem; width: 100%;"/>
        <br>
        <SkeletonPlaceholder style="height: 10rem; width: 100%;"/>

    </TileGroup>


{:else}
    <div className="center">
        <div>
            <RadioButtonGroup>
                <DataTableSkeleton
                        headers={[
                                        { value: "Nome" },
                                        { value: "Ultimo Intervento" , sort: false},
                                        { value: "Distanza in Giorni" },
                                        {value: "Avvisi"},
                                        { empty: true },
                                      ]}
                        rows={10}
                />
            </RadioButtonGroup>

        </div>
    </div>
{/if}


<style>

    .radioWrapper {
        display: flex;
        align-items: flex-start;
        justify-content: left;
        margin: 0;
    }

    .center {
        margin: auto;
        width: auto;

        padding: 10px;
        display: flex;
        justify-content: center;
    }

    .vertical-center {
        margin: 0;

    }


    .rightAlign {
        margin: auto;
        width: auto;

        padding: 10px;
        display: flex;
        justify-content: right;
    }

    .content {
        display: grid;
        grid-template-columns: 80% 20%;
        grid-column-gap: 0px;
    }


</style>
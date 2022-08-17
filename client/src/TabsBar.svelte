<script>
    import {AppBar, Icon, Tab, Tabs} from 'svelte-materialify';
    import { ProgressLinear } from 'svelte-materialify';
    import { Button } from "carbon-components-svelte";
    import Renew from "carbon-icons-svelte/lib/Renew.svelte";
    import {mdiClipboardTextClock, mdiCloudDownload, mdiCog, mdiHome, mdiPlusBox} from '@mdi/js';
    import {
        mobileMode,
        selectedMeteoStation,
        valueMain,
        valueMeteo,
        online,
        valueLimnimetri,
        selectedLimnimetriStation, valueDeflussiMinimi, selectedDeflussiMinimiStation
    } from "./Stores/store";
    console.log($selectedMeteoStation)

    export let loadingProgress = 0;
    export let setupProgress = 0;



</script>


<AppBar>

    <span slot="title">
         {#if $valueMain === 0}
            {#if $selectedMeteoStation.name === "" }
                Survey Notes
            {:else}
                Survey Notes per {$selectedMeteoStation.name}
            {/if}
         {:else if  $valueMain === 1}
              Survey Notes
         {:else if  $valueMain === 2}
              Survey Notes
         {:else if  $valueMain === 3}
              Survey Notes
         {/if}

    </span>

    <div style="flex-grow:1"></div>
    <Button disabled={!$online}
            iconDescription="Sincronizza Manualmente"
            tooltipPosition="left"
            on:click={function (){location.reload();}}
            icon={Renew} />

    <div slot="extension">
        <ProgressLinear color="blue"  backgroundColor="blue" bind:value={loadingProgress} bind:buffer={setupProgress} stream />

        <Tabs class="blue-text" bind:value={$valueMain} grow fixedTabs>

            <div slot="tabs">
                <Tab> <txt class:smallTxt="{$mobileMode}">Stazioni Meteo</txt></Tab>
                <Tab><txt class:smallTxt="{$mobileMode}">Deflussi Minimi</txt></Tab>
                <Tab><txt class:smallTxt="{$mobileMode}">Limnimetri</txt></Tab>
            </div>
        </Tabs>


        {#if $valueMain === 0}
            <Tabs icons grow bind:value={$valueMeteo} class="blue-text">
                <div slot="tabs">
                    <Tab>
                        <Icon path={mdiHome} />
                    </Tab>
                        <Tab disabled={$selectedMeteoStation.name === ""}>
                            <Icon path={mdiClipboardTextClock} />
                        </Tab>
                        <Tab disabled={$selectedMeteoStation.name === ""}>
                            <Icon path={mdiPlusBox} />
                        </Tab>
                </div>
            </Tabs>
        {:else if $valueMain === 1}
            <Tabs icons grow bind:value={$valueLimnimetri} class="blue-text">
                <div slot="tabs">
                    <Tab>
                        <Icon path={mdiHome} />
                    </Tab>
                    <Tab disabled={$selectedLimnimetriStation.name === ""}>
                        <Icon path={mdiClipboardTextClock} />
                    </Tab>
                    <Tab disabled={$selectedLimnimetriStation.name === ""}>
                        <Icon path={mdiPlusBox} />
                    </Tab>
                </div>
            </Tabs>
        {:else if $valueMain === 2}
            <Tabs icons grow bind:value={$valueDeflussiMinimi} class="blue-text">
                <div slot="tabs">
                    <Tab>
                        <Icon path={mdiHome} />
                    </Tab>
                    <Tab disabled={$selectedDeflussiMinimiStation.name === ""}>
                        <Icon path={mdiClipboardTextClock} />
                    </Tab>
                    <Tab disabled={$selectedDeflussiMinimiStation.name === ""}>
                        <Icon path={mdiPlusBox} />
                    </Tab>
                </div>
            </Tabs>
        {/if}


    </div>
</AppBar>



<style>
    .smallTxt{
        font-size: 10px;
    }
</style>

<script>
    import {Window, WindowItem } from 'svelte-materialify';

    import {valueDeflussiMinimi, valueLimnimetri, valueMain} from "./Stores/store";
    import { valueMeteo } from "./Stores/store";
    import StazioneMeteoForm from "./StazioneMeteo/StazioneMeteoForm.svelte";
    import StazioneMeteoHistory from "./StazioneMeteo/StazioneMeteoHistory.svelte";
    import StazioniMeteoMain from "./StazioneMeteo/StazioniMeteoMain.svelte";
    import DeflussiMinimiMain from "./DeflussiMinimi/DeflussiMinimiMain.svelte";
    import DeflussiMinimiHistory from "./DeflussiMinimi/DeflussiMinimiHistory.svelte";
    import DeflussiMinimiForm from "./DeflussiMinimi/DeflussiMinimiForm.svelte";
    import LimnimetriMain from "./Limnimetri/LimnimetriMain.svelte";
    import LimnimetriHistory from "./Limnimetri/LimnimetriHistory.svelte";
    import LimnimetriForm from "./Limnimetri/LimnimetriForm.svelte";


</script>

<Window value={$valueMain} class="ma-2">
    <WindowItem>
        <Window value={$valueMeteo} class="ma-2">
            <WindowItem>
                <StazioniMeteoMain></StazioniMeteoMain>
            </WindowItem>
            <WindowItem>
                <StazioneMeteoHistory></StazioneMeteoHistory>
            </WindowItem>
            <WindowItem>
                <StazioneMeteoForm></StazioneMeteoForm>
            </WindowItem>
        </Window>

    </WindowItem>
    <WindowItem>
        <Window value={$valueDeflussiMinimi} class="ma-2">
            <WindowItem>
                <DeflussiMinimiMain></DeflussiMinimiMain>
            </WindowItem>
            <WindowItem>
                <DeflussiMinimiHistory></DeflussiMinimiHistory>
            </WindowItem>
            <WindowItem>
                <DeflussiMinimiForm></DeflussiMinimiForm>
            </WindowItem>
        </Window>
    </WindowItem>
    <WindowItem>
        <Window value={$valueLimnimetri} class="ma-2">
            <WindowItem>
                <LimnimetriMain></LimnimetriMain>
            </WindowItem>
            <WindowItem>
                <LimnimetriHistory></LimnimetriHistory>
            </WindowItem>
            <WindowItem>
                <LimnimetriForm></LimnimetriForm>
            </WindowItem>
        </Window>
    </WindowItem>
</Window>
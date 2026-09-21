<script context="module">
  // Module-only setup must remain separate from the instance script.
  export function configure(value) {
    return value + 1;
  }
</script>

<script lang="ts">
  // This comment should not become part of an extracted body.
  function process(value: number): string {
    if (value > 0) {
      return `value:${value}`;
    }
    return "empty";
  }

  const decorate = (value: string) => {
    return value.trim();
  };
</script>

<style>
  .card { color: rebeccapurple; }
  @keyframes ignored { from { opacity: 0; } to { opacity: 1; } }
</style>

{#if ready}
  <!-- Template markup is not indexed. -->
  <p>Ready</p>
{/if}

<button onclick={(event: MouseEvent) => save(event, process(1))}>Save</button>
<button on:click={() => cancel()}>Cancel</button>

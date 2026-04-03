{/*
  Client showcase component.
  2-column grid cards with logo on top, links stacked below description.
  Defaults to shuffled order for fairness; toggle to switch to alphabetical.
*/}
export const ClientShowcase = ({clients}) => {
  const shuffle = (arr) => {
    const copy = arr.slice();
    for (let i = copy.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  };

  const sort = (clients) => clients.toSorted((a, b) => a.name.localeCompare(b.name));

  const [state, dispatch] = React.useReducer((state, action) => {
    switch (action) {
      case "shuffle": return { mode: "shuffle", clients: shuffle(clients) };
      case "alpha":   return { mode: "alpha", clients: sort(clients) };
      default:        return state;
    }
  }, { mode: "shuffle", clients: shuffle(clients) });

  const Logo = ({ client }) => (
    <a href={client.url} className="block no-underline border-none w-full h-full">
      <img className="block dark:hidden object-contain w-full h-full !my-0" src={client.lightSrc} alt={client.name} noZoom />
      <img className="hidden dark:block object-contain w-full h-full !my-0" src={client.darkSrc} alt={client.name} noZoom />
    </a>
  );

  const ToggleButton = ({ active, onClick, icon, title }) => (
    <button
      onClick={onClick}
      title={title}
      className={`px-3 py-1 cursor-pointer border-none ${
        active
          ? 'bg-gray-200 dark:bg-gray-600'
          : 'hover:bg-gray-100 dark:hover:bg-gray-800'
      }`}
    >
      <Icon icon={icon} size={16} />
    </button>
  );

  return (
    <div>
      <div className="flex justify-end mb-3">
        <div className="inline-flex rounded-md border border-gray-200 dark:border-gray-700 overflow-hidden">
          <ToggleButton active={state.mode === "shuffle"} onClick={() => dispatch("shuffle")} icon="shuffle" title="Shuffle" />
          <ToggleButton active={state.mode === "alpha"} onClick={() => dispatch("alpha")} icon="arrow-down-a-z" title="Alphabetical" />
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {state.clients.map(client => (
          <div key={client.name} className="border border-gray-200 dark:border-gray-700 rounded-lg px-5 py-3 flex flex-col">
            <div className="mx-auto mb-1.5" style={{height: 80, width: 150 * (client.scale || 1)}}>
              <Logo client={client} />
            </div>
            <div className="text-base font-semibold mb-1.5"><a href={client.url}>{client.name}</a></div>
            <p className="text-sm text-gray-600 dark:text-gray-400 m-0 leading-normal flex-1">{client.description}</p>
            {(client.instructionsUrl || client.sourceCodeUrl) && (
              <div className="border-t border-gray-100 dark:border-gray-800 -mx-5 -mb-3 mt-3 px-5 py-3 bg-gray-50 dark:bg-gray-800/50 rounded-b-lg text-sm text-gray-500 dark:text-gray-400 flex flex-wrap gap-x-5 gap-y-1">
                {client.instructionsUrl && (
                  <span className="whitespace-nowrap">
                    <Icon icon="gear" size={14} /> <a href={client.instructionsUrl} className="text-gray-500 dark:text-gray-400">Setup instructions</a>
                  </span>
                )}
                {client.sourceCodeUrl && (
                  <span className="whitespace-nowrap">
                    <Icon icon="code" size={14} /> <a href={client.sourceCodeUrl} className="text-gray-500 dark:text-gray-400">Source code</a>
                  </span>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

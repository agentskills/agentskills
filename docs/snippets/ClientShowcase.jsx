{/*
  Client showcase component.
  2-column grid cards with logo on top, links stacked below description.
*/}
export const ClientShowcase = ({clients}) => {
  const sorted = clients.slice().sort((a, b) => a.name.localeCompare(b.name));

  const Logo = ({ client }) => (
    <a href={client.url} className="block no-underline border-none w-full h-full">
      <img className="block dark:hidden object-contain w-full h-full !my-0" src={client.lightSrc} alt={client.name} noZoom />
      <img className="hidden dark:block object-contain w-full h-full !my-0" src={client.darkSrc} alt={client.name} noZoom />
    </a>
  );

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      {sorted.map(client => (
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
  );
};

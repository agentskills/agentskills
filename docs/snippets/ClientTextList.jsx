{/*
  Plain-text adoption list rendered from the shared clients data.
  Always alphabetical and static (no shuffle), so the list is stable
  for crawlers and LLM-based consumers of the docs.
*/}
export const ClientTextList = ({clients}) => {
  const sorted = clients.toSorted((a, b) => a.name.localeCompare(b.name));
  return (
    <ul>
      {sorted.map(client => (
        <li key={client.name}>
          <a href={client.url}>{client.name}</a>
          {client.sourceCodeUrl && (
            <> (<a href={client.sourceCodeUrl}>source code</a>)</>
          )}
          {client.description && (
            <> — {client.description}</>
          )}
        </li>
      ))}
    </ul>
  );
};

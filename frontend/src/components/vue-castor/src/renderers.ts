
import { customRenderers } from './custom';
import { layoutRenderers } from './layouts';

export const castorRenderers = [
  ...customRenderers,
  ...layoutRenderers,
];
